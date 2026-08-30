from sqlalchemy.orm import Session
from database import DBNetworkEvent
from datetime import datetime, timedelta

def gather_deep_context(db: Session, host_id: str, destination: str, current_timestamp: datetime, lookback_days: int = 7):
    """
    On-Demand Deep Context Gathering: Only triggers if the quick checks raise suspicion.
    Fetches historical events for the same host + destination over the lookback period.
    """
    start_time = current_timestamp - timedelta(days=lookback_days)
    
    events = db.query(DBNetworkEvent).filter(
        DBNetworkEvent.host_id == host_id,
        DBNetworkEvent.dst_ip == destination,
        DBNetworkEvent.timestamp >= start_time,
        DBNetworkEvent.timestamp <= current_timestamp
    ).order_by(DBNetworkEvent.timestamp.asc()).all()
    
    return events
