"""
Temporal Correlation Engine — the core of LeakSignal.

Connects individually harmless events over time by analyzing:
- Same host + same destination across multiple events
- Temporal clustering (similar hours across days)
- Volume patterns (consistently elevated or growing)
- Day-over-day persistence
"""


def correlate_events(events: list) -> dict:
    """
    Analyzes a set of historical events for the same host+destination pair.
    Returns correlation signals that feed into ERS calculation.
    
    Args:
        events: List of DBNetworkEvent objects for same host + destination,
                ordered chronologically.
    
    Returns:
        dict with correlation signals and metadata.
    """
    if not events or len(events) < 2:
        return {
            "is_correlated": False,
            "event_count": len(events) if events else 0,
            "distinct_days": 0,
            "is_growing_volume": False,
            "is_temporal_cluster": False,
            "hour_consistency": 0.0,
            "volume_trend": 0.0,
            "correlation_strength": 0.0,
        }

    # --- Basic counts ---
    event_count = len(events)
    distinct_days = len(set(e.timestamp.date() for e in events))
    distinct_hours = len(set(e.timestamp.hour for e in events))

    # --- Temporal clustering ---
    # Are events happening at similar hours across different days?
    hours = [e.timestamp.hour for e in events]
    if distinct_days >= 2 and distinct_hours <= 3:
        is_temporal_cluster = True
    else:
        is_temporal_cluster = False

    # Hour consistency: ratio of most-common hour to total events
    from collections import Counter
    hour_counts = Counter(hours)
    most_common_count = hour_counts.most_common(1)[0][1] if hour_counts else 0
    hour_consistency = most_common_count / event_count if event_count > 0 else 0

    # --- Volume analysis ---
    volumes = [e.bytes_sent for e in events]
    avg_volume = sum(volumes) / len(volumes) if volumes else 0

    # Is volume growing over time? (simple linear trend)
    if len(volumes) >= 3:
        # Compare first half avg to second half avg
        mid = len(volumes) // 2
        first_half_avg = sum(volumes[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(volumes[mid:]) / (len(volumes) - mid) if (len(volumes) - mid) > 0 else 0
        if first_half_avg > 0:
            volume_trend = (second_half_avg - first_half_avg) / first_half_avg
        else:
            volume_trend = 0.0
        is_growing_volume = volume_trend > 0.15  # >15% growth
    else:
        volume_trend = 0.0
        is_growing_volume = False

    # --- Correlation strength (0.0 - 1.0) ---
    strength = 0.0

    # More events = stronger correlation
    if event_count >= 3:
        strength += min(0.25, (event_count - 2) * 0.08)

    # Multi-day persistence
    if distinct_days >= 2:
        strength += min(0.30, (distinct_days - 1) * 0.10)

    # Temporal clustering
    if is_temporal_cluster:
        strength += 0.20

    # Hour consistency
    strength += min(0.15, hour_consistency * 0.20)

    # Growing volume
    if is_growing_volume:
        strength += 0.10

    strength = min(1.0, strength)

    is_correlated = (
        event_count >= 3
        and distinct_days >= 2
        and strength >= 0.35
    )

    return {
        "is_correlated": is_correlated,
        "event_count": event_count,
        "distinct_days": distinct_days,
        "distinct_hours": distinct_hours,
        "is_growing_volume": is_growing_volume,
        "is_temporal_cluster": is_temporal_cluster,
        "hour_consistency": round(hour_consistency, 3),
        "volume_trend": round(volume_trend, 3),
        "correlation_strength": round(strength, 3),
        "avg_volume_bytes": int(avg_volume),
    }
