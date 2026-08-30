import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal, DBHost, DBAlert

def trigger_demo_anomalies():
    db = SessionLocal()
    
    # 1. Update FIN-PC-07 (Slow-Drip)
    fin_host = db.query(DBHost).filter(DBHost.host_id == "FIN-PC-07").first()
    if fin_host:
        fin_host.risk_state = "Possible Slow Data Exfiltration"
        
        # Create Alert
        alert1 = DBAlert(
            alert_id="ALT-20260904-001",
            host_id="FIN-PC-07",
            classification="Slow Data Exfiltration",
            ers_score=91,
            severity="Critical",
            explanation="Volume anomaly detected: 5-8MB sent to uncategorized destination outside of normal working hours across 4 consecutive nights.",
            status="Open",
            created_at=datetime.now(),
            evidence={"signal": "repeated_off_hours", "dest": "104.28.14.99"}
        )
        db.merge(alert1)

    # 2. Update HR-PC-02 (New Dest + Off-Hours)
    hr_host = db.query(DBHost).filter(DBHost.host_id == "HR-PC-02").first()
    if hr_host:
        hr_host.risk_state = "Suspicious"
        
        # Create Alert
        alert2 = DBAlert(
            alert_id="ALT-20260904-002",
            host_id="HR-PC-02",
            classification="Suspicious Activity",
            ers_score=75,
            severity="High",
            explanation="Single massive transfer (12MB) to a first-seen destination at 2:15 AM.",
            status="Open",
            created_at=datetime.now(),
            evidence={"signal": "first_seen_dest", "dest": "8.8.8.8"}
        )
        db.merge(alert2)
        
    db.commit()
    print("Demo ML triggers applied successfully. Dashboard will now show critical alerts.")
    db.close()

if __name__ == "__main__":
    trigger_demo_anomalies()
