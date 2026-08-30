from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, DBAlert

router = APIRouter()

@router.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(DBAlert).all()
    return [
        {
            "alert_id": a.alert_id,
            "host_id": a.host_id,
            "classification": a.classification,
            "ers": a.ers_score,
            "created_at": str(a.created_at),
            "summary": a.explanation
        } for a in alerts
    ]

@router.get("/api/alerts/{alert_id}")
def get_alert_detail(alert_id: str, db: Session = Depends(get_db)):
    a = db.query(DBAlert).filter(DBAlert.alert_id == alert_id).first()
    
    # PT1 UI has a hardcoded sidebar link to ALRT-1042. 
    # If our dynamic dataset didn't generate that exact ID, grab the highest risk alert instead.
    if not a and alert_id == "ALRT-1042":
        a = db.query(DBAlert).order_by(DBAlert.ers_score.desc()).first()
        
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    evidence = dict(a.evidence) if a.evidence else {}
    signals_dict = evidence.get("signals", {})
    
    signals_list = []
    if signals_dict.get("new_destination"):
        signals_list.append({"id": "sig-1", "name": "First-seen destination", "description": "Destination has not appeared in the host profile before.", "severity": "high"})
    if signals_dict.get("off_hours"):
        signals_list.append({"id": "sig-2", "name": "Off-hours transfer", "description": "Transfer occurred outside the host's normal active hours.", "severity": "high"})
    if signals_dict.get("repeated_transfers"):
        signals_list.append({"id": "sig-3", "name": "Repeated sessions", "description": "Similar outbound sessions repeated.", "severity": "critical"})
    if signals_dict.get("multi_day_persistence"):
        signals_list.append({"id": "sig-4", "name": "Multi-day persistence", "description": "The pattern persisted long enough to indicate slow-drip behavior.", "severity": "critical"})
    if signals_dict.get("volume_deviation"):
        signals_list.append({"id": "sig-5", "name": "Volume Deviation", "description": "Transfer size deviates from normal behavior.", "severity": "medium"})

    fp_check = evidence.get("false_positive_check", {})
    
    return {
        "alert_id": a.alert_id,
        "host_id": a.host_id,
        "classification": a.classification,
        "ers": a.ers_score,
        "created_at": str(a.created_at),
        "signals": signals_list,
        "false_positive_check": {
            "approved_destination": fp_check.get("known_legitimate_pattern", False),
            "scheduled_backup": fp_check.get("known_legitimate_pattern", False),
            "result": "Legitimate pattern found" if fp_check.get("known_legitimate_pattern") else "No legitimate explanation found"
        }
    }
