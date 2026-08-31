from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, DBHost, DBAlert, DBHostProfile

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


@router.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    monitored = db.query(DBHost).count()

    # Count from actual ERS per host (same source as /api/hosts)
    critical = 0
    suspicious = 0
    hosts = db.query(DBHost).all()
    for h in hosts:
        _, classification = _get_real_ers(db, h.host_id)
        if classification == "Possible Slow Data Exfiltration":
            critical += 1
        elif classification == "Suspicious":
            suspicious += 1

    alerts_today = db.query(DBAlert).count()

    return {
        "monitored_hosts": monitored,
        "critical_hosts": critical,
        "suspicious_hosts": suspicious,
        "monitor_hosts": 0,
        "alerts_today": alerts_today,
    }
