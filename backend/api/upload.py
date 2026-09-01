from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, DBNetworkEvent, DBAlert, DBHostProfile, DBERSHistory
from ingestion.csv_loader import process_csv_stream
from profiles.host_identity import resolve_host
from profiles.host_profile import get_or_create_profile, update_host_profile
from detection.quick_checks import check_event_context
from detection.suspicion_gate import evaluate_suspicion
from detection.deep_context import gather_deep_context
from detection.repetition import analyze_repetition
from detection.persistence import analyze_persistence
from detection.correlation import correlate_events
from detection.false_positive import check_false_positives
from risk.ers import calculate_ers
import io
from datetime import datetime

router = APIRouter()


def run_detection_pipeline(db: Session, events: list[dict]) -> dict:
    """
    Shared detection pipeline — processes typed event dicts through the full
    detection engine. Used by both /api/upload and /api/reload.
    Returns summary dict.
    """

    # Group events by host for per-host daily ERS tracking
    host_daily_ers: dict[str, dict[str, dict]] = {}  # {host_id: {day_str: {score, classification, signals}}}

    for row in events:
        # 1. Host Identity
        host = resolve_host(db, row['host_id'], row['src_ip'], row['timestamp'])

        # 2. Get current profile (BEFORE any updates)
        profile = get_or_create_profile(db, host.host_id)

        # 3. Quick Context Checks (using EXISTING baseline — event NOT yet added)
        context_flags = check_event_context(
            row['timestamp'].hour,
            row['dst_ip'],
            row['bytes_sent'],
            profile.baseline_metrics
        )

        # 4. Suspicion Gate
        pre_score, requires_deep_path = evaluate_suspicion(context_flags)

        if requires_deep_path:
            # === DEEP PATH — suspicious event detected ===

            # 5. Save the suspicious event to DB (so deep context can find it)
            db_event = DBNetworkEvent(
                host_id=host.host_id,
                timestamp=row['timestamp'],
                src_ip=row['src_ip'],
                dst_ip=row['dst_ip'],
                port=row['dst_port'],
                protocol=row['protocol'],
                bytes_sent=row['bytes_sent'],
                duration=row['duration'],
                destination_category=row['destination_category']
            )
            db.add(db_event)
            db.commit()

            # 6. Deep Context — gather historical events for same host+dest
            historical_events = gather_deep_context(db, host.host_id, row['dst_ip'], row['timestamp'])

            # 7. Repetition and Persistence
            is_repeated = analyze_repetition(historical_events)
            is_persistent = analyze_persistence(historical_events)

            # 8. Temporal Correlation
            correlation = correlate_events(historical_events)

            # 9. False Positive Check
            fp_flags = check_false_positives(row)

            # 10. Build ERS signals
            signals = {
                "new_destination": context_flags.get("is_first_seen_dest"),
                "rare_destination": context_flags.get("is_rare_destination"),
                "off_hours": context_flags.get("is_off_hours"),
                "volume_deviation": context_flags.get("is_transfer_deviation"),
                "external_destination": context_flags.get("is_external_destination", False),
                "repeated_transfers": is_repeated,
                "multi_day_persistence": is_persistent,
                "temporal_correlation": correlation.get("is_correlated", False),
                "growing_volume": correlation.get("is_growing_volume", False),
                "known_legitimate_pattern": fp_flags.get("known_legitimate_pattern"),
            }

            # 11. Calculate real ERS
            final_ers, classification = calculate_ers(signals)

            # 12. Persist ERS on host profile (keep highest — worst-case posture)
            if final_ers > (profile.current_ers or 0):
                profile.current_ers = final_ers
                profile.current_classification = classification
                host.risk_state = classification

            # DO NOT update baseline with suspicious event — prevents poisoning

            db.commit()

            # 13. Track daily ERS for timeline
            day_str = row['timestamp'].strftime("%Y-%m-%d")
            if host.host_id not in host_daily_ers:
                host_daily_ers[host.host_id] = {}
            # Keep the highest ERS per day (worst case)
            existing = host_daily_ers[host.host_id].get(day_str)
            if not existing or final_ers > existing["ers"]:
                host_daily_ers[host.host_id][day_str] = {
                    "ers": final_ers,
                    "classification": classification,
                    "signals": signals,
                    "timestamp": row['timestamp'],
                }

            # 14. Generate Alert if classification warrants it
            if classification in ["Suspicious", "Possible Slow Data Exfiltration"]:
                alert = DBAlert(
                    alert_id=f"ALRT-{db_event.event_id}",
                    host_id=host.host_id,
                    classification=classification,
                    ers_score=final_ers,
                    severity="high" if classification == "Suspicious" else "critical",
                    explanation=f"Detected pattern to {row['dst_ip']} — {classification}",
                    status="Open",
                    created_at=row['timestamp'],
                    evidence={
                        "signals": signals,
                        "false_positive_check": fp_flags,
                        "correlation": {
                            "event_count": correlation.get("event_count", 0),
                            "distinct_days": correlation.get("distinct_days", 0),
                            "hour_consistency": correlation.get("hour_consistency", 0),
                            "volume_trend": correlation.get("volume_trend", 0),
                            "strength": correlation.get("correlation_strength", 0),
                        },
                        "context": context_flags,
                    }
                )
                db.add(alert)
                db.commit()

        else:
            # === FAST PATH — normal event ===
            # Save the event
            db_event = DBNetworkEvent(
                host_id=host.host_id,
                timestamp=row['timestamp'],
                src_ip=row['src_ip'],
                dst_ip=row['dst_ip'],
                port=row['dst_port'],
                protocol=row['protocol'],
                bytes_sent=row['bytes_sent'],
                duration=row['duration'],
                destination_category=row['destination_category']
            )
            db.add(db_event)
            db.commit()

            # Update baseline ONLY with normal events
            profile = update_host_profile(
                db, host.host_id,
                row['bytes_sent'], row['timestamp'].hour, row['dst_ip']
            )

    # --- Post-processing: Write ERS history records per host per day ---
    for host_id, daily_data in host_daily_ers.items():
        for day_str, day_info in daily_data.items():
            # Check if we already have a record for this host+day
            existing = db.query(DBERSHistory).filter(
                DBERSHistory.host_id == host_id,
                DBERSHistory.day_label == day_str
            ).first()

            if existing:
                # Update if new score is higher
                if day_info["ers"] > existing.ers_score:
                    existing.ers_score = day_info["ers"]
                    existing.classification = day_info["classification"]
                    existing.signals = day_info["signals"]
            else:
                history = DBERSHistory(
                    host_id=host_id,
                    timestamp=day_info["timestamp"],
                    day_label=day_str,
                    ers_score=day_info["ers"],
                    classification=day_info["classification"],
                    signals=day_info["signals"],
                )
                db.add(history)

    db.commit()

    # --- Summary (count from alerts — profile.current_classification may lag) ---
    from sqlalchemy import func
    total_hosts = db.query(DBHostProfile).count()

    # Get max ERS per host from alerts
    host_max_ers = db.query(
        DBAlert.host_id,
        func.max(DBAlert.ers_score).label("max_ers")
    ).group_by(DBAlert.host_id).all()

    critical = sum(1 for _, max_ers in host_max_ers if max_ers >= 75)
    suspicious = sum(1 for _, max_ers in host_max_ers if 50 <= max_ers < 75)
    normal = total_hosts - critical - suspicious

    return {
        "status": "success",
        "message": f"Processed {len(events)} events — {total_hosts} hosts analyzed, "
                   f"{critical} critical, {suspicious} suspicious",
        "events_processed": len(events),
        "hosts_analyzed": total_hosts,
        "critical_hosts": critical,
        "suspicious_hosts": suspicious,
    }


@router.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        file_stream = io.StringIO(content.decode("utf-8"))
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Expected UTF-8 CSV.")

    events = process_csv_stream(file_stream)

    if not events:
        raise HTTPException(status_code=400, detail="CSV contains no valid events.")

    return run_detection_pipeline(db, events)
