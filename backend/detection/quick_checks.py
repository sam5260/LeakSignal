def check_event_context(event_hour: int, destination: str, bytes_sent: int, baseline: dict) -> dict:
    """
    Performs a fast initial check of an event against the host's persistent baseline.
    Avoids expensive database queries.
    """
    context = {
        "is_off_hours": False,
        "is_first_seen_dest": False,
        "is_transfer_deviation": False
    }
    
    if not baseline:
        return context
        
    # Check off-hours (if active hours exist and event hour is not in them)
    active_hours = baseline.get("active_hours", [])
    if active_hours and event_hour not in active_hours:
        context["is_off_hours"] = True
        
    # Check first-seen destination
    known_dests = baseline.get("known_destinations", [])
    if known_dests and destination not in known_dests:
        context["is_first_seen_dest"] = True
        
    # Check transfer deviation (e.g. > 2x the normal average)
    avg_bytes = baseline.get("avg_bytes_per_transfer", 0)
    if avg_bytes > 0 and bytes_sent > (avg_bytes * 2):
        context["is_transfer_deviation"] = True
        
    return context
