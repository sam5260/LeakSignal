import csv
from datetime import datetime
import sys
import os

# Add parent dir to path so we can import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal, DBNetworkEvent, DBHost

def load_csv_to_db(csv_path):
    db = SessionLocal()
    
    # First, let's clear existing data so we don't duplicate on multiple runs
    db.query(DBNetworkEvent).delete()
    db.commit()

    print(f"Loading data from {csv_path}...")
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        events = []
        hosts = set()
        
        for row in reader:
            # Ensure host exists in DBHost table first
            if row['host_id'] not in hosts:
                existing_host = db.query(DBHost).filter(DBHost.host_id == row['host_id']).first()
                if not existing_host:
                    new_host = DBHost(
                        host_id=row['host_id'],
                        hostname=row['host_id'],
                        current_ip=row['src_ip'],
                        first_seen=datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S"),
                        last_seen=datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S"),
                        risk_state="Normal"
                    )
                    db.add(new_host)
                hosts.add(row['host_id'])
            
            # Create network event
            event = DBNetworkEvent(
                host_id=row['host_id'],
                timestamp=datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S"),
                src_ip=row['src_ip'],
                dst_ip=row['dst_ip'],
                port=row['port'],
                protocol=row['protocol'],
                bytes_sent=int(row['bytes_sent']),
                bytes_received=int(row['bytes_received']),
                duration=int(row['duration']),
                destination_category=row['destination_category']
            )
            events.append(event)
            
        db.commit() # Commit hosts
        
        # Bulk insert network events
        db.bulk_save_objects(events)
        db.commit()
        
    print(f"Successfully loaded {len(events)} network events into the database.")
    db.close()

def process_csv_stream(file_stream):
    reader = csv.DictReader(file_stream)
    events = []
    for row in reader:
        events.append({
            'host_id': row['host_id'],
            'timestamp': datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S"),
            'src_ip': row['src_ip'],
            'dst_ip': row['dst_ip'],
            'dst_port': int(row['port']),
            'protocol': row['protocol'],
            'bytes_sent': int(row['bytes_sent']),
            'bytes_received': int(row['bytes_received']),
            'duration': int(row['duration']),
            'destination_category': row['destination_category']
        })
    return events

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, "demo_data", "dataset.csv")
    if os.path.exists(csv_file):
        load_csv_to_db(csv_file)
    else:
        print("Dataset not found. Run generate_dataset.py first.")
