from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import get_db, DBNetworkEvent, DBAlert
from ingestion.csv_loader import process_csv_stream
from profiles.host_identity import resolve_host
from profiles.host_profile import update_host_profile
from detection.quick_checks import check_event_context
from detection.suspicion_gate import evaluate_suspicion
from detection.deep_context import gather_deep_context
from detection.repetition import analyze_repetition
from detection.persistence import analyze_persistence
from detection.false_positive import check_false_positives
from risk.ers import calculate_ers
import io

router = APIRouter()

@router.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    file_stream = io.StringIO(content.decode("utf-8"))
    
    events = process_csv_stream(file_stream)
    
    for row in events:
        # 1. Host Identity
        host = resolve_host(db, row['host_id'], row['src_ip'], row['timestamp'])
        
        # Get current profile BEFORE updating to properly detect first-seen/off-hours
        from profiles.host_profile import get_or_create_profile
        profile = get_or_create_profile(db, host.host_id)
        
        # 4. Quick Context Checks (using existing baseline)
        context_flags = check_event_context(
            row['timestamp'].hour, 
            row['dst_ip'], 
            row['bytes_sent'], 
            profile.baseline_metrics
        )
        
        # 2. Update Baseline Profile (incorporate new event)
        profile = update_host_profile(db, host.host_id, row['bytes_sent'], row['timestamp'].hour, row['dst_ip'])
        
        # 3. Save Event to DB
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
        db.commit() # Commit so deep context can find it
        
        # 5. Suspicion Gate
        pre_score, requires_deep_path = evaluate_suspicion(context_flags)
        
        if requires_deep_path:
            # 6. Deep Context
            historical_events = gather_deep_context(db, host.host_id, row['dst_ip'], row['timestamp'])
            
            # 7 & 8. Repetition and Persistence
            is_repeated = analyze_repetition(historical_events)
            is_persistent = analyze_persistence(historical_events)
            
            # 9. False Positive
            fp_flags = check_false_positives(row)
            
            # 10 & 11. ERS and Final Decision
            signals = {
                "new_destination": context_flags.get("is_first_seen_dest"),
                "off_hours": context_flags.get("is_off_hours"),
                "volume_deviation": context_flags.get("is_transfer_deviation"),
                "repeated_transfers": is_repeated,
                "multi_day_persistence": is_persistent,
                "known_legitimate_pattern": fp_flags.get("known_legitimate_pattern")
            }
            
            final_ers, classification = calculate_ers(signals)
            
            # 12. Update host risk state (always take highest risk or newest state for PT1 demo)
            host.risk_state = classification
            profile.recent_risk_state = classification
            db.commit()
            
            # Generate Alert if necessary
            if classification in ["Suspicious", "Possible Slow Data Exfiltration"]:
                alert = DBAlert(
                    alert_id=f"ALRT-{db_event.event_id}",
                    host_id=host.host_id,
                    classification=classification,
                    ers_score=final_ers,
                    severity="high" if classification == "Suspicious" else "critical",
                    explanation=f"Detected pattern to {row['dst_ip']}",
                    status="Open",
                    created_at=row['timestamp'],
                    evidence={"signals": signals, "false_positive_check": fp_flags}
                )
                db.add(alert)
                db.commit()
                
        else:
            # ONLY update the baseline if the event is considered normal (fast path passed)
            # This prevents anomalous events from poisoning the host's behavioral baseline.
            profile = update_host_profile(db, host.host_id, row['bytes_sent'], row['timestamp'].hour, row['dst_ip'])

    return {"status": "success", "message": "Dataset uploaded and processed successfully"}
