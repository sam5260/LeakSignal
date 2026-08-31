import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# Absolute DB path — no more cwd-dependent duplicates
_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(_DB_DIR, exist_ok=True)
_DB_PATH = os.path.join(_DB_DIR, "leaksignal.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class DBHost(Base):
    __tablename__ = "hosts"
    host_id = Column(String, primary_key=True, index=True)
    hostname = Column(String)
    department = Column(String)
    current_ip = Column(String)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    risk_state = Column(String, default="Normal")


class DBNetworkEvent(Base):
    __tablename__ = "network_events"
    event_id = Column(Integer, primary_key=True, index=True)
    host_id = Column(String, ForeignKey("hosts.host_id"))
    timestamp = Column(DateTime, index=True)
    src_ip = Column(String)
    dst_ip = Column(String)
    port = Column(String)
    protocol = Column(String)
    bytes_sent = Column(Integer)
    bytes_received = Column(Integer)
    duration = Column(Integer)
    destination_category = Column(String)


class DBHostProfile(Base):
    __tablename__ = "host_profiles"
    host_id = Column(String, ForeignKey("hosts.host_id"), primary_key=True)
    baseline_metrics = Column(JSON)
    active_hour_profile = Column(JSON)
    destination_summary = Column(JSON)
    transfer_behaviour = Column(JSON)
    recent_risk_state = Column(String)
    current_ers = Column(Integer, default=0)
    current_classification = Column(String, default="Normal")


class DBERSHistory(Base):
    """Tracks ERS score per host per processing day for timeline graphs."""
    __tablename__ = "ers_history"
    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(String, ForeignKey("hosts.host_id"), index=True)
    timestamp = Column(DateTime)
    day_label = Column(String)
    ers_score = Column(Integer)
    classification = Column(String)
    signals = Column(JSON)


class DBAlert(Base):
    __tablename__ = "alerts"
    alert_id = Column(String, primary_key=True, index=True)
    host_id = Column(String, ForeignKey("hosts.host_id"))
    classification = Column(String)
    ers_score = Column(Integer)
    severity = Column(String)
    explanation = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    evidence = Column(JSON)


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_database():
    """Drop all data for clean demo re-run. Preserves schema."""
    db = SessionLocal()
    try:
        db.query(DBERSHistory).delete()
        db.query(DBAlert).delete()
        db.query(DBHostProfile).delete()
        db.query(DBNetworkEvent).delete()
        db.query(DBHost).delete()
        db.commit()
    finally:
        db.close()
