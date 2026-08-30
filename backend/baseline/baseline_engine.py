def update_baseline(baseline: dict, bytes_sent: int, hour: int, destination: str) -> dict:
    """
    Updates the host's behavioral baseline incrementally without requiring full history scans.
    """
    # Initialize if empty
    if not baseline:
        baseline = {
            "total_events": 0,
            "avg_bytes_per_transfer": 0,
            "known_destinations": [],
            "active_hours": []
        }
    
    # Update event counts and rolling average bytes
    prev_total = baseline.get("total_events", 0)
    prev_avg = baseline.get("avg_bytes_per_transfer", 0)
    
    new_total = prev_total + 1
    new_avg = prev_avg + ((bytes_sent - prev_avg) / new_total)
    
    baseline["total_events"] = new_total
    baseline["avg_bytes_per_transfer"] = new_avg
    
    # Update known destinations (keep top 100 for PT1 memory control)
    known_dests = set(baseline.get("known_destinations", []))
    known_dests.add(destination)
    baseline["known_destinations"] = list(known_dests)[:100]
    
    # Update active hours (simple tracking of hours seen)
    active_hours = set(baseline.get("active_hours", []))
    active_hours.add(hour)
    baseline["active_hours"] = list(active_hours)
    
    return baseline
