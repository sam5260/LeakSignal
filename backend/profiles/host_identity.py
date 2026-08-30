from sqlalchemy.orm import Session
from database import DBHost
from datetime import datetime

def resolve_host(db: Session, host_id: str, src_ip: str, timestamp: datetime) -> DBHost:
    """
    Identifies the host using a stable host identity and retains IP as network context.
    If the host doesn't exist, it creates it. Updates last_seen and current_ip.
    """
    host = db.query(DBHost).filter(DBHost.host_id == host_id).first()
    
    if not host:
        # Determine department based on host_id prefix for baseline grouping
        department = "Unknown"
        if host_id.startswith("FIN"):
            department = "Finance"
        elif host_id.startswith("HR"):
            department = "HR"
        elif host_id.startswith("DEV"):
            department = "Development"
        elif host_id.startswith("BACKUP"):
            department = "Infrastructure"

        host = DBHost(
            host_id=host_id,
            hostname=host_id.lower(),
            department=department,
            current_ip=src_ip,
            first_seen=timestamp,
            last_seen=timestamp,
            risk_state="Normal"
        )
        db.add(host)
    else:
        # Update context
        host.current_ip = src_ip
        if timestamp > host.last_seen:
            host.last_seen = timestamp
            
    db.commit()
    db.refresh(host)
    return host
