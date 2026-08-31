from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db, DBHost, DBAlert, DBHostProfile
from datetime import datetime

router = APIRouter()


@router.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    monitored = db.query(DBHost).count()

    # Count from alerts (max ERS per host) — profiles may lag behind
    host_max_ers = db.query(
        DBAlert.host_id,
        func.max(DBAlert.ers_score).label("max_ers")
    ).group_by(DBAlert.host_id).all()

    critical = sum(1 for _, max_ers in host_max_ers if max_ers >= 75)
    suspicious = sum(1 for _, max_ers in host_max_ers if 50 <= max_ers < 75)
    total_alert_hosts = len(host_max_ers)
    normal = monitored - total_alert_hosts
    alerts_today = db.query(DBAlert).count()

    return {
        "monitored_hosts": monitored,
        "critical_hosts": critical,
        "suspicious_hosts": suspicious,
        "monitor_hosts": 0,
        "alerts_today": alerts_today,
    }
