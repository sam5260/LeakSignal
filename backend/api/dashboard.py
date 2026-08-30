from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, DBHost, DBAlert
from datetime import datetime

router = APIRouter()

@router.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    monitored = db.query(DBHost).count()
    critical = db.query(DBHost).filter(DBHost.risk_state == "Possible Slow Data Exfiltration").count()
    suspicious = db.query(DBHost).filter(DBHost.risk_state == "Suspicious").count()
    
    # Simple count of all alerts for PT1
    alerts_today = db.query(DBAlert).count()
    
    return {
        "monitored_hosts": monitored,
        "critical_hosts": critical,
        "suspicious_hosts": suspicious,
        "alerts_today": alerts_today
    }
