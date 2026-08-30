from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, DBHost, DBHostProfile, DBNetworkEvent

router = APIRouter()

@router.get("/api/hosts")
def get_hosts(db: Session = Depends(get_db)):
    hosts = db.query(DBHost).all()
    results = []
    for h in hosts:
        # Get ERS from profile if it exists, otherwise default
        profile = db.query(DBHostProfile).filter(DBHostProfile.host_id == h.host_id).first()
        # In a real app we'd store the exact current ERS score on the host or profile.
        # For PT1, we estimate from risk_state.
        ers_mock = 0
        if h.risk_state == "Possible Slow Data Exfiltration":
            ers_mock = 91
        elif h.risk_state == "Suspicious":
            ers_mock = 65
        elif h.risk_state == "Monitor":
            ers_mock = 35
            
        results.append({
            "host_id": h.host_id,
            "ers": ers_mock,
            "classification": h.risk_state,
            "last_seen": str(h.last_seen),
            "department": h.department
        })
    return results

@router.get("/api/hosts/{host_id}")
def get_host_detail(host_id: str, db: Session = Depends(get_db)):
    h = db.query(DBHost).filter(DBHost.host_id == host_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Host not found")
        
    profile = db.query(DBHostProfile).filter(DBHostProfile.host_id == host_id).first()
    baseline = profile.baseline_metrics if profile and profile.baseline_metrics else {}
    
    avg_bytes = baseline.get("avg_bytes_per_transfer", 0) / (1024*1024) # MB
    
    ers_mock = 0
    if h.risk_state == "Possible Slow Data Exfiltration":
        ers_mock = 91
    elif h.risk_state == "Suspicious":
        ers_mock = 65
    elif h.risk_state == "Monitor":
        ers_mock = 35
        
    return {
        "host_id": h.host_id,
        "ers": ers_mock,
        "classification": h.risk_state,
        "classification_label": h.risk_state,
        "department": h.department,
        "last_seen": str(h.last_seen),
        "baseline_outbound_mb": round(avg_bytes, 2),
        "current_outbound_mb": round(avg_bytes * 1.5, 2), # Mocked for PT1
        "deviation_pct": 50,
        "new_destination": "N/A",
        "destination_status": "known",
        "repeated_nights": 0,
        "outbound_comparison": []
    }

@router.get("/api/hosts/{host_id}/timeline")
def get_host_timeline(host_id: str, db: Session = Depends(get_db)):
    # Mocking timeline progression based on final state
    h = db.query(DBHost).filter(DBHost.host_id == host_id).first()
    if not h:
        return []
        
    if h.risk_state == "Possible Slow Data Exfiltration":
        return [
            { "day": "Day 1", "date": "Day 1", "ers": 31, "classification": "Monitor" },
            { "day": "Day 2", "date": "Day 2", "ers": 48, "classification": "Monitor" },
            { "day": "Day 3", "date": "Day 3", "ers": 69, "classification": "Suspicious" },
            { "day": "Day 4", "date": "Day 4", "ers": 91, "classification": "Possible Slow Data Exfiltration" }
        ]
    return [
        { "day": "Day 1", "date": "Day 1", "ers": 10, "classification": "Normal" }
    ]
