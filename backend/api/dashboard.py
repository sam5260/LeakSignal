from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, DBHost, DBAlert, DBHostProfile
from datetime import datetime

router = APIRouter()


@router.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    monitored = db.query(DBHost).count()
    critical = db.query(DBHostProfile).filter(
        DBHostProfile.current_classification == "Possible Slow Data Exfiltration"
    ).count()
    suspicious = db.query(DBHostProfile).filter(
        DBHostProfile.current_classification == "Suspicious"
    ).count()
    monitor = db.query(DBHostProfile).filter(
        DBHostProfile.current_classification == "Monitor"
    ).count()
    alerts_today = db.query(DBAlert).count()

    return {
        "monitored_hosts": monitored,
        "critical_hosts": critical,
        "suspicious_hosts": suspicious,
        "monitor_hosts": monitor,
        "alerts_today": alerts_today,
    }
