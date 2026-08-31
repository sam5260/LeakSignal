def update_baseline(baseline: dict, bytes_sent: int, hour: int, destination: str) -> dict:
    """
    Incremental baseline update. Only called for NORMAL events.
    Tracks frequency distributions, not just boolean presence.
    """
    if not baseline:
        baseline = {
            "total_events": 0,
            "avg_bytes_per_transfer": 0,
            "bytes_m2": 0,  # Welford's M2 for variance
            "known_destinations": {},  # {dest: count}
            "active_hours": {},  # {hour: count}
            "peak_hour_count": 0,
        }

    # --- Event count & Welford's online variance ---
    prev_total = baseline.get("total_events", 0)
    prev_avg = baseline.get("avg_bytes_per_transfer", 0)
    prev_m2 = baseline.get("bytes_m2", 0)

    new_total = prev_total + 1
    delta = bytes_sent - prev_avg
    new_avg = prev_avg + delta / new_total
    delta2 = bytes_sent - new_avg
    new_m2 = prev_m2 + delta * delta2

    baseline["total_events"] = new_total
    baseline["avg_bytes_per_transfer"] = new_avg
    baseline["bytes_m2"] = new_m2

    # Standard deviation (derived, not stored — computed on read)
    # baseline["std_bytes"] = sqrt(new_m2 / new_total) when needed

    # --- Destination frequency ---
    dests = dict(baseline.get("known_destinations", {}))
    dests[destination] = dests.get(destination, 0) + 1
    # Cap at 200 entries, evict lowest-count when full
    if len(dests) > 200:
        sorted_dests = sorted(dests.items(), key=lambda x: x[1])
        for k, _ in sorted_dests[:50]:
            del dests[k]
    baseline["known_destinations"] = dests

    # --- Hour frequency ---
    hours = dict(baseline.get("active_hours", {}))
    hours[hour] = hours.get(hour, 0) + 1
    baseline["active_hours"] = hours

    # Track peak hour for normalization
    if hours:
        baseline["peak_hour_count"] = max(hours.values())

    return baseline


def get_hour_frequency(baseline: dict, hour: int) -> float:
    """Returns 0.0-1.0 — how frequent this hour is relative to peak."""
    hours = baseline.get("active_hours", {})
    if not hours:
        return 0.0
    peak = baseline.get("peak_hour_count", max(hours.values()) if hours else 1)
    return hours.get(hour, 0) / max(peak, 1)


def get_destination_frequency(baseline: dict, destination: str) -> float:
    """Returns 0.0-1.0 — how frequent this destination is relative to most common."""
    dests = baseline.get("known_destinations", {})
    if not dests:
        return 0.0
    peak = max(dests.values()) if dests else 1
    return dests.get(destination, 0) / max(peak, 1)


def get_std_bytes(baseline: dict) -> float:
    """Returns standard deviation of bytes per transfer."""
    import math
    total = baseline.get("total_events", 0)
    m2 = baseline.get("bytes_m2", 0)
    if total < 2:
        return 0.0
    return math.sqrt(m2 / total)
