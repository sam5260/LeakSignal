from sqlalchemy.orm import Session
from database import DBHostProfile
from baseline.baseline_engine import update_baseline

def get_or_create_profile(db: Session, host_id: str) -> DBHostProfile:
    profile = db.query(DBHostProfile).filter(DBHostProfile.host_id == host_id).first()
    if not profile:
        profile = DBHostProfile(
            host_id=host_id,
            baseline_metrics={},
            active_hour_profile={},
            destination_summary={},
            transfer_behaviour={},
            recent_risk_state="Normal"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

def update_host_profile(db: Session, host_id: str, bytes_sent: int, hour: int, destination: str):
    profile = get_or_create_profile(db, host_id)
    
    # Extract current dictionary (SQLAlchemy JSON requires explicit reassignment or mutator flags to detect changes)
    current_baseline = dict(profile.baseline_metrics) if profile.baseline_metrics else {}
    
    # Update through the baseline engine
    new_baseline = update_baseline(current_baseline, bytes_sent, hour, destination)
    
    profile.baseline_metrics = new_baseline
    db.commit()
    db.refresh(profile)
    return profile
