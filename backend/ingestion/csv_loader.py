import csv
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal, DBNetworkEvent, DBHost


def validate_row(row: dict) -> dict | None:
    """Validate and normalize a single CSV row. Returns None if invalid."""
    try:
        required = ['host_id', 'timestamp', 'src_ip', 'dst_ip', 'bytes_sent']
        if not all(k in row and row[k].strip() for k in required):
            return None

        ts = datetime.strptime(row['timestamp'].strip(), "%Y-%m-%d %H:%M:%S")
        bytes_sent = int(row['bytes_sent'].strip())
        if bytes_sent < 0:
            return None

        return {
            'host_id': row['host_id'].strip(),
            'timestamp': ts,
            'src_ip': row['src_ip'].strip(),
            'dst_ip': row['dst_ip'].strip(),
            'dst_port': int(row.get('port', '0').strip() or '0'),
            'protocol': row.get('protocol', 'TCP').strip().upper(),
            'bytes_sent': bytes_sent,
            'bytes_received': int(row.get('bytes_received', '0').strip() or '0'),
            'duration': int(row.get('duration', '0').strip() or '0'),
            'destination_category': row.get('destination_category', 'Unknown').strip(),
        }
    except (ValueError, KeyError):
        return None


def load_csv_to_db(csv_path):
    """Bulk-load CSV to DB. Clears existing data first for clean demo."""
    db = SessionLocal()

    # Clear all data for clean re-run
    db.query(DBNetworkEvent).delete()
    db.query(DBHost).delete()
    db.commit()

    print(f"Loading data from {csv_path}...")

    valid_count = 0
    invalid_count = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        hosts = {}
        events = []

        for row_num, row in enumerate(reader, start=2):
            validated = validate_row(row)
            if not validated:
                invalid_count += 1
                continue

            valid_count += 1

            # Create host if new
            host_id = validated['host_id']
            if host_id not in hosts:
                existing = db.query(DBHost).filter(DBHost.host_id == host_id).first()
                if not existing:
                    # Derive department
                    department = "Unknown"
                    if host_id.startswith("FIN"):
                        department = "Finance"
                    elif host_id.startswith("HR"):
                        department = "HR"
                    elif host_id.startswith("DEV"):
                        department = "Development"
                    elif host_id.startswith("BACKUP"):
                        department = "Infrastructure"

                    new_host = DBHost(
                        host_id=host_id,
                        hostname=host_id.lower(),
                        department=department,
                        current_ip=validated['src_ip'],
                        first_seen=validated['timestamp'],
                        last_seen=validated['timestamp'],
                        risk_state="Normal"
                    )
                    db.add(new_host)
                    hosts[host_id] = True

            events.append(DBNetworkEvent(
                host_id=host_id,
                timestamp=validated['timestamp'],
                src_ip=validated['src_ip'],
                dst_ip=validated['dst_ip'],
                port=str(validated['dst_port']),
                protocol=validated['protocol'],
                bytes_sent=validated['bytes_sent'],
                bytes_received=validated['bytes_received'],
                duration=validated['duration'],
                destination_category=validated['destination_category'],
            ))

    db.commit()

    if events:
        db.bulk_save_objects(events)
        db.commit()

    print(f"Loaded {valid_count} valid events, {invalid_count} invalid rows skipped.")
    db.close()
    return valid_count


def process_csv_stream(file_stream):
    """Parse CSV stream into typed event dicts. Returns only valid rows."""
    reader = csv.DictReader(file_stream)
    events = []
    for row in reader:
        validated = validate_row(row)
        if validated:
            events.append(validated)
    return events


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, "demo_data", "dataset.csv")
    if os.path.exists(csv_file):
        load_csv_to_db(csv_file)
    else:
        print("Dataset not found. Run generate_dataset.py first.")
