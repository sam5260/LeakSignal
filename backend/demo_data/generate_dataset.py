import csv
import random
from datetime import datetime, timedelta
import os

# Scenarios from PDF:
# A: Slow-Drip: FIN-PC-07 sends 5-8 MB to same unusual dest at night.
# B: New Dest + Off-Hours: HR-PC-02 sends 12 MB to first-seen at 2:15 AM.
# C: False Positive Backup: BACKUP-SERVER-01 sends 400-600 MB every night.

HEADERS = [
    "host_id", "timestamp", "src_ip", "dst_ip", "port", "protocol", 
    "bytes_sent", "bytes_received", "duration", "destination_category"
]

def generate_timestamp(base_date, hour, minute_range=(0,59)):
    return base_date.replace(hour=hour, minute=random.randint(*minute_range), second=random.randint(0, 59))

def generate_normal_traffic(host, src_ip, base_date):
    events = []
    for hour in range(9, 18):
        for _ in range(random.randint(1, 5)):
            ts = generate_timestamp(base_date, hour)
            dst_ip = f"10.0.0.{random.randint(10, 50)}" 
            events.append({
                "host_id": host,
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "port": random.choice(["443", "80"]),
                "protocol": "TCP",
                "bytes_sent": random.randint(1000, 500000), 
                "bytes_received": random.randint(5000, 1000000),
                "duration": random.randint(1, 120),
                "destination_category": "Known"
            })
    return events

def main():
    start_date = datetime(2026, 9, 1) 
    all_events = []
    
    hosts = [
        ("FIN-PC-07", "192.168.1.107"),
        ("HR-PC-02", "192.168.1.102"),
        ("BACKUP-SERVER-01", "192.168.1.200"),
        ("DEV-PC-01", "192.168.1.50")
    ]
    
    for day_offset in range(4):
        current_date = start_date + timedelta(days=day_offset)
        
        for host, ip in hosts:
            all_events.extend(generate_normal_traffic(host, ip, current_date))
            
        # Scenario A: Slow-Drip
        ts_a = generate_timestamp(current_date, random.choice([2, 3])) 
        all_events.append({
            "host_id": "FIN-PC-07",
            "timestamp": ts_a.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": "192.168.1.107",
            "dst_ip": "104.28.14.99", 
            "port": "443",
            "protocol": "TCP",
            "bytes_sent": random.randint(5000000, 8000000),
            "bytes_received": random.randint(1000, 5000),
            "duration": random.randint(300, 600),
            "destination_category": "Uncategorized"
        })
        
        # Scenario B: New Dest + Off-Hours
        if day_offset == 3: 
            ts_b = generate_timestamp(current_date, 2, (15, 20)) 
            all_events.append({
                "host_id": "HR-PC-02",
                "timestamp": ts_b.strftime("%Y-%m-%d %H:%M:%S"),
                "src_ip": "192.168.1.102",
                "dst_ip": "8.8.8.8", 
                "port": "443",
                "protocol": "TCP",
                "bytes_sent": 12500000, 
                "bytes_received": random.randint(1000, 5000),
                "duration": random.randint(400, 800),
                "destination_category": "Uncategorized"
            })
            
        # Scenario C: Legitimate Backup
        ts_c = generate_timestamp(current_date, 1) 
        all_events.append({
            "host_id": "BACKUP-SERVER-01",
            "timestamp": ts_c.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": "192.168.1.200",
            "dst_ip": "52.216.146.90", 
            "port": "443",
            "protocol": "TCP",
            "bytes_sent": random.randint(400000000, 600000000), 
            "bytes_received": random.randint(5000, 10000),
            "duration": random.randint(1800, 3600),
            "destination_category": "Approved Cloud Provider"
        })

    all_events.sort(key=lambda x: x["timestamp"])
    
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset.csv")
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(all_events)
        
    print(f"Generated {len(all_events)} events in {output_path}")

if __name__ == "__main__":
    main()
