import csv
import random
from datetime import datetime, timedelta
import os

HEADERS = [
    "host_id", "timestamp", "src_ip", "dst_ip", "port", "protocol",
    "bytes_sent", "bytes_received", "duration", "destination_category"
]

# --- Consistent destination pools per host ---
# Each host talks to its own set of internal servers during business hours.
# This way the baseline learns solid known destinations.

FIN_NORMAL_DESTS = [
    ("10.0.0.20", "Known"),    # Financial DB server
    ("10.0.0.30", "Known"),    # Print server
    ("10.0.0.40", "Known"),    # File server
    ("10.0.0.25", "Known"),    # ERP system
    ("10.0.0.35", "Known"),    # Email gateway
]

HR_NORMAL_DESTS = [
    ("10.0.0.21", "Known"),    # HR DB server
    ("10.0.0.31", "Known"),    # Payroll system
    ("10.0.0.41", "Known"),    # Document server
    ("10.0.0.26", "Known"),    # Benefits portal
    ("10.0.0.36", "Known"),    # Training platform
]

DEV_NORMAL_DESTS = [
    ("10.0.0.22", "Known"),    # Git server
    ("10.0.0.32", "Known"),    # Docker registry
    ("10.0.0.42", "Known"),    # CI/CD server
    ("10.0.0.27", "Known"),    # Staging server
    ("10.0.0.37", "Known"),    # Dev database
    ("10.0.0.47", "Known"),    # Package mirror
    ("10.0.0.52", "Known"),    # API gateway
]

BACKUP_NORMAL_DESTS = [
    ("10.0.0.25", "Known"),    # Backup NAS
    ("10.0.0.35", "Known"),    # Monitoring server
    ("10.0.0.45", "Known"),    # Logging server
]

HOST_DESTS = {
    "FIN-PC-07": FIN_NORMAL_DESTS,
    "HR-PC-02": HR_NORMAL_DESTS,
    "DEV-PC-01": DEV_NORMAL_DESTS,
    "BACKUP-SERVER-01": BACKUP_NORMAL_DESTS,
}


def generate_timestamp(base_date, hour, minute_range=(0, 59)):
    return base_date.replace(
        hour=hour,
        minute=random.randint(*minute_range),
        second=random.randint(0, 59)
    )


def generate_normal_traffic(host, src_ip, base_date):
    """Normal business-hours traffic: 9AM-6PM, using CONSISTENT destination IPs."""
    events = []
    dests = HOST_DESTS[host]

    for hour in range(9, 18):
        for _ in range(random.randint(2, 4)):
            ts = generate_timestamp(base_date, hour)
            # Pick from the host's consistent pool (occasionally mix in a new one for realism)
            if random.random() < 0.9:
                dst_ip, category = random.choice(dests)
            else:
                # 10% chance: new internal IP (simulates occasional new server)
                dst_ip = f"10.0.0.{random.randint(60, 99)}"
                category = "Known"
            events.append({
                "host_id": host,
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "port": random.choice(["443", "80"]),
                "protocol": "TCP",
                "bytes_sent": random.randint(1000, 500_000),
                "bytes_received": random.randint(5000, 1_000_000),
                "duration": random.randint(1, 120),
                "destination_category": category,
            })
    return events


def main():
    start_date = datetime(2026, 9, 1)
    all_events = []

    hosts = [
        ("FIN-PC-07", "192.168.1.107"),
        ("HR-PC-02", "192.168.1.102"),
        ("BACKUP-SERVER-01", "192.168.1.200"),
        ("DEV-PC-01", "192.168.1.50"),
    ]

    for day_offset in range(7):  # 7 days: 3 warm-up + 4 attack
        current_date = start_date + timedelta(days=day_offset)

        # Everyone gets normal traffic every day
        for host, ip in hosts:
            all_events.extend(generate_normal_traffic(host, ip, current_date))

        # --- BACKUP-SERVER-01: Legitimate nightly backup (all 7 days) ---
        ts_c = generate_timestamp(current_date, 1)
        all_events.append({
            "host_id": "BACKUP-SERVER-01",
            "timestamp": ts_c.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": "192.168.1.200",
            "dst_ip": "52.216.146.90",
            "port": "443",
            "protocol": "TCP",
            "bytes_sent": random.randint(400_000_000, 600_000_000),
            "bytes_received": random.randint(5000, 10000),
            "duration": random.randint(1800, 3600),
            "destination_category": "Approved Cloud Provider",
        })

        # --- FIN-PC-07: Slow-drip exfiltration (starts day 3 = offset 3) ---
        if day_offset >= 3:
            ts_a = generate_timestamp(current_date, random.choice([2, 3]))
            all_events.append({
                "host_id": "FIN-PC-07",
                "timestamp": ts_a.strftime("%Y-%m-%d %H:%M:%S"),
                "src_ip": "192.168.1.107",
                "dst_ip": "104.28.14.99",
                "port": "443",
                "protocol": "TCP",
                "bytes_sent": random.randint(5_000_000, 8_000_000),
                "bytes_received": random.randint(1000, 5000),
                "duration": random.randint(300, 600),
                "destination_category": "Uncategorized",
            })

        # --- HR-PC-02: Single large off-hours transfer (day 5 only) ---
        if day_offset == 5:
            ts_b = generate_timestamp(current_date, 2, (15, 20))
            all_events.append({
                "host_id": "HR-PC-02",
                "timestamp": ts_b.strftime("%Y-%m-%d %H:%M:%S"),
                "src_ip": "192.168.1.102",
                "dst_ip": "8.8.8.8",
                "port": "443",
                "protocol": "TCP",
                "bytes_sent": 12_500_000,
                "bytes_received": random.randint(1000, 5000),
                "duration": random.randint(400, 800),
                "destination_category": "Uncategorized",
            })

    all_events.sort(key=lambda x: x["timestamp"])

    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset.csv")

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(all_events)

    print(f"Generated {len(all_events)} events over 7 days in {output_path}")

    from collections import Counter
    host_counts = Counter(e["host_id"] for e in all_events)
    print("\nPer-host event counts:")
    for h, c in sorted(host_counts.items()):
        print(f"  {h}: {c}")

    fin_night = sum(1 for e in all_events if e["host_id"] == "FIN-PC-07" and e["timestamp"][11:13] in ("02", "03") and e["dst_ip"] == "104.28.14.99")
    print(f"\nFIN-PC-07 suspicious night events: {fin_night}")
    hr_night = sum(1 for e in all_events if e["host_id"] == "HR-PC-02" and e["dst_ip"] == "8.8.8.8")
    print(f"HR-PC-02 suspicious events: {hr_night}")


if __name__ == "__main__":
    main()
