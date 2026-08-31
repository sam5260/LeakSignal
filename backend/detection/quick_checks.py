from baseline.baseline_engine import get_hour_frequency, get_destination_frequency, get_std_bytes


def _is_internal_ip(dst_ip: str) -> bool:
    """Check if an IP is in a private/internal range."""
    if not dst_ip:
        return False
    parts = dst_ip.split(".")
    if len(parts) != 4:
        return False
    try:
        first, second = int(parts[0]), int(parts[1])
        if first == 10:
            return True
        if first == 172 and 16 <= second <= 31:
            return True
        if first == 192 and second == 168:
            return True
        if first == 127:
            return True
    except ValueError:
        pass
    return False


def check_event_context(event_hour: int, destination: str, bytes_sent: int, baseline: dict) -> dict:
    """
    Fast-path checks against the host's persistent baseline.
    Returns flags and raw values for downstream ERS calculation.
    """
    context = {
        "is_off_hours": False,
        "is_first_seen_dest": False,
        "is_transfer_deviation": False,
        "is_rare_destination": False,
        "is_external_destination": False,
        "hour_frequency": 0.0,
        "dest_frequency": 0.0,
        "deviation_ratio": 0.0,
    }

    # Flag external destinations (non-internal IPs are more suspicious)
    context["is_external_destination"] = not _is_internal_ip(destination)

    if not baseline or baseline.get("total_events", 0) < 10:
        # Not enough baseline data — can't judge yet
        return context

    # --- Hour frequency ---
    hour_freq = get_hour_frequency(baseline, event_hour)
    context["hour_frequency"] = hour_freq
    # Off-hours = this hour has < 5% of peak activity
    if hour_freq < 0.05:
        context["is_off_hours"] = True

    # --- Destination frequency ---
    dest_freq = get_destination_frequency(baseline, destination)
    context["dest_frequency"] = dest_freq

    known_dests = baseline.get("known_destinations", {})
    num_known = len(known_dests)

    if destination not in known_dests:
        # First-seen destination — flag if host has established baseline
        if num_known < 50:
            context["is_first_seen_dest"] = True
        elif dest_freq == 0:
            context["is_rare_destination"] = True
    elif num_known > 15:
        # Known but rare (only flag if host has enough diversity for this to matter)
        dest_count = known_dests.get(destination, 0)
        if dest_count <= 1:
            context["is_rare_destination"] = True

    # --- Transfer deviation ---
    avg_bytes = baseline.get("avg_bytes_per_transfer", 0)
    std_bytes = get_std_bytes(baseline)
    if avg_bytes > 0 and std_bytes > 0 and std_bytes > avg_bytes * 0.1:
        deviation_ratio = (bytes_sent - avg_bytes) / std_bytes
        context["deviation_ratio"] = deviation_ratio
        # Flag if > 3 standard deviations above mean
        if deviation_ratio > 3.0:
            context["is_transfer_deviation"] = True
    elif avg_bytes > 0:
        # No variance data — use 5x threshold
        if bytes_sent > avg_bytes * 5:
            context["is_transfer_deviation"] = True

    return context
