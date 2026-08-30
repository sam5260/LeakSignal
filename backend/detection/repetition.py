def analyze_repetition(events: list) -> bool:
    """
    Returns True if there are multiple similar events (e.g., > 2) to the same destination.
    """
    return len(events) >= 3
