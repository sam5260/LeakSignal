from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, DBHost, DBHostProfile, DBNetworkEvent, DBERSHistory, DBAlert
from baseline.baseline_engine import get_std_bytes

router = APIRouter()


def _get_real_ers(db: Session, host_id: str) -> tuple[int, str]:
    """Get the real ERS from the highest-scoring alert for this host."""
    alert = db.query(DBAlert).filter(
        DBAlert.host_id == host_id
    ).order_by(DBAlert.ers_score.desc()).first()

    if alert:
        return alert.ers_score, alert.classification

    # Fallback: from profile
    profile = db.query(DBHostProfile).filter(DBHostProfile.host_id == host_id).first()
    if profile:
        return profile.current_ers or 0, profile.current_classification or "Normal"
    return 0, "Normal"


@router.get("/api/hosts")
def get_hosts(db: Session = Depends(get_db)):
    hosts = db.query(DBHost).all()
    results = []
    for h in hosts:
        ers, classification = _get_real_ers(db, h.host_id)

        results.append({
            "host_id": h.host_id,
            "ers": ers,
            "classification": classification,
            "last_seen": str(h.last_seen),
            "department": h.department,
        })
    return results


@router.get("/api/hosts/{host_id}")
def get_host_detail(host_id: str, db: Session = Depends(get_db)):
    h = db.query(DBHost).filter(DBHost.host_id == host_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Host not found")

    profile = db.query(DBHostProfile).filter(DBHostProfile.host_id == host_id).first()
    baseline = profile.baseline_metrics if profile and profile.baseline_metrics else {}

    avg_bytes = baseline.get("avg_bytes_per_transfer", 0)
    avg_mb = avg_bytes / (1024 * 1024)

    # Get real ERS from alerts
    ers, classification = _get_real_ers(db, host_id)

    # Get ALL events first for comprehensive analysis
    from collections import Counter
    all_events = db.query(DBNetworkEvent).filter(
        DBNetworkEvent.host_id == host_id
    ).all()

    # Get recent events for current outbound calculation
    recent_events = db.query(DBNetworkEvent).filter(
        DBNetworkEvent.host_id == host_id
    ).order_by(DBNetworkEvent.timestamp.desc()).limit(10).all()

    if recent_events:
        current_avg = sum(e.bytes_sent for e in recent_events) / len(recent_events)
        current_mb = current_avg / (1024 * 1024)
        deviation_pct = ((current_avg - avg_bytes) / avg_bytes * 100) if avg_bytes > 0 else 0
    else:
        current_mb = avg_mb
        deviation_pct = 0

    # **FIX**: For high-risk hosts, identify the THREAT destination (uncategorized/external)
    # not just the most recent event's destination
    known_dests = baseline.get("known_destinations", {}) or {}
    
    if ers >= 50:  # High-risk host - find threat destination
        # Priority 1: Uncategorized destinations (external threat)
        uncategorized = [e for e in all_events if e.destination_category == "Uncategorized"]
        if uncategorized:
            threat_event = uncategorized[0]  # First uncategorized destination
            last_destination = threat_event.dst_ip
            dest_category = "Uncategorized"
            dest_status = "uncategorized"
        else:
            # Priority 2: First-seen destinations (not in baseline)
            unknown = [e for e in all_events if e.dst_ip not in known_dests]
            if unknown:
                threat_event = unknown[0]
                last_destination = threat_event.dst_ip
                dest_category = threat_event.destination_category or "Unknown"
                dest_status = "first-seen"
            else:
                # Fallback: most recent
                last_event = recent_events[0] if recent_events else all_events[0]
                last_destination = last_event.dst_ip
                dest_category = last_event.destination_category or "Unknown"
                dest_status = "known"
    else:
        # Normal/low-risk host - use most recent event
        if recent_events:
            last_event = recent_events[0]
            last_destination = last_event.dst_ip
            dest_category = last_event.destination_category or "Unknown"
            if isinstance(known_dests, dict):
                dest_status = "first-seen" if last_destination not in known_dests else "known"
            else:
                dest_status = "unknown"
        else:
            last_destination = "N/A"
            dest_category = "Unknown"
            dest_status = "unknown"

    # Count off-hours sessions from all events
    hours = [e.timestamp.hour for e in all_events]
    hour_counts = Counter(hours)
    peak = max(hour_counts.values()) if hour_counts else 1
    off_hours_count = sum(
        count for hour, count in hour_counts.items()
        if count / peak < 0.05 and count > 0
    )

    # Build outbound comparison from daily aggregates
    from collections import defaultdict
    daily_volumes = defaultdict(list)
    for e in all_events:
        day = e.timestamp.strftime("%Y-%m-%d")
        daily_volumes[day].append(e.bytes_sent)

    outbound_comparison = []
    for day in sorted(daily_volumes.keys()):
        day_avg = sum(daily_volumes[day]) / len(daily_volumes[day])
        outbound_comparison.append({
            "label": day,
            "baselineMB": round(avg_mb, 2),
            "currentMB": round(day_avg / (1024 * 1024), 2),
        })

    # Classification label
    label_map = {
        "Normal": "Normal",
        "Monitor": "Monitor",
        "Suspicious": "Suspicious",
        "Possible Slow Data Exfiltration": "Possible Slow Data Exfiltration",
    }

    return {
        "host_id": h.host_id,
        "ers": ers,
        "classification": classification,
        "classification_label": label_map.get(classification, classification),
        "department": h.department,
        "last_seen": str(h.last_seen),
        "baseline_outbound_mb": round(avg_mb, 2),
        "current_outbound_mb": round(current_mb, 2),
        "deviation_pct": round(deviation_pct, 1),
        "new_destination": last_destination,
        "destination_status": dest_status,
        "destination_category": dest_category,
        "repeated_nights": off_hours_count,
        "unique_destinations": len(set(e.dst_ip for e in all_events)),
        "total_events": len(all_events),
        "outbound_comparison": outbound_comparison,
    }


@router.get("/api/hosts/{host_id}/timeline")
def get_host_timeline(host_id: str, db: Session = Depends(get_db)):
    """Returns real ERS history from DB."""
    h = db.query(DBHost).filter(DBHost.host_id == host_id).first()
    if not h:
        return []

    history = db.query(DBERSHistory).filter(
        DBERSHistory.host_id == host_id
    ).order_by(DBERSHistory.day_label.asc()).all()

    if history:
        return [
            {
                "day": record.day_label,
                "date": record.day_label,
                "ers": record.ers_score,
                "classification": record.classification,
            }
            for record in history
        ]

    # Fallback: build from raw events
    events = db.query(DBNetworkEvent).filter(
        DBNetworkEvent.host_id == host_id
    ).order_by(DBNetworkEvent.timestamp.asc()).all()

    if not events:
        return []

    from collections import defaultdict
    daily = defaultdict(list)
    for e in events:
        daily[e.timestamp.date()].append(e)

    return [
        {"day": str(day), "date": str(day), "ers": 10, "classification": "Normal"}
        for day in sorted(daily.keys())
    ]
