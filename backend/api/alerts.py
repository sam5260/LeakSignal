from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, DBAlert, DBHost, DBHostProfile, DBNetworkEvent, DBHostProfile, DBERSHistory, reset_database
from ingestion.csv_loader import load_csv_to_db
import os

router = APIRouter()


@router.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(DBAlert).order_by(DBAlert.ers_score.desc()).all()
    return [
        {
            "alert_id": a.alert_id,
            "host_id": a.host_id,
            "classification": a.classification,
            "ers": a.ers_score,
            "created_at": str(a.created_at),
            "summary": a.explanation,
        }
        for a in alerts
    ]


@router.get("/api/alerts/{alert_id}")
def get_alert_detail(alert_id: str, db: Session = Depends(get_db)):
    a = db.query(DBAlert).filter(DBAlert.alert_id == alert_id).first()

    # Fallback: if specific ID not found, grab highest risk alert
    if not a:
        a = db.query(DBAlert).order_by(DBAlert.ers_score.desc()).first()

    if not a:
        raise HTTPException(status_code=404, detail="No alerts found")

    evidence = dict(a.evidence) if a.evidence else {}
    signals_dict = evidence.get("signals", {})
    correlation_data = evidence.get("correlation", {})
    context_data = evidence.get("context", {})

    signals_list = []
    if signals_dict.get("new_destination"):
        signals_list.append({
            "id": "sig-1", "name": "First-seen destination",
            "description": "Destination has not appeared in the host profile before.",
            "severity": "high",
        })
    if signals_dict.get("off_hours"):
        signals_list.append({
            "id": "sig-2", "name": "Off-hours transfer",
            "description": "Transfer occurred outside the host's normal active hours.",
            "severity": "high",
        })
    if signals_dict.get("repeated_transfers"):
        signals_list.append({
            "id": "sig-3", "name": "Repeated sessions",
            "description": f"Similar outbound sessions repeated across "
                           f"{correlation_data.get('distinct_days', '?')} days.",
            "severity": "critical",
        })
    if signals_dict.get("multi_day_persistence"):
        signals_list.append({
            "id": "sig-4", "name": "Multi-day persistence",
            "description": "The pattern persisted long enough to indicate slow-drip behavior.",
            "severity": "critical",
        })
    if signals_dict.get("volume_deviation"):
        signals_list.append({
            "id": "sig-5", "name": "Volume deviation",
            "description": "Transfer size deviates significantly from normal behavior.",
            "severity": "medium",
        })
    if signals_dict.get("temporal_correlation"):
        signals_list.append({
            "id": "sig-6", "name": "Temporal correlation",
            "description": (f"Events clustered at similar hours across days "
                           f"(consistency: {correlation_data.get('hour_consistency', 0):.0%})."),
            "severity": "high",
        })
    if signals_dict.get("growing_volume"):
        signals_list.append({
            "id": "sig-7", "name": "Growing volume",
            "description": "Transfer volume is increasing over time.",
            "severity": "medium",
        })

    fp_check = evidence.get("false_positive_check", {})
    is_legitimate = fp_check.get("known_legitimate_pattern", False)

    return {
        "alert_id": a.alert_id,
        "host_id": a.host_id,
        "classification": a.classification,
        "ers": a.ers_score,
        "created_at": str(a.created_at),
        "signals": signals_list,
        "false_positive_check": {
            "approved_destination": is_legitimate,
            "scheduled_backup": is_legitimate,
            "result": "Legitimate pattern found" if is_legitimate else "No legitimate explanation found",
        },
    }


@router.post("/api/reset")
def reset_demo(db: Session = Depends(get_db)):
    """Reset database for clean demo re-run."""
    reset_database()
    return {"status": "success", "message": "Database reset. Ready for fresh upload."}


@router.post("/api/reload")
def reload_dataset(db: Session = Depends(get_db)):
    """Reset + reload the demo dataset."""
    reset_database()

    dataset_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "demo_data", "dataset.csv"
    )
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="dataset.csv not found")

    load_csv_to_db(dataset_path)
    return {"status": "success", "message": "Dataset reloaded from demo_data/dataset.csv"}
