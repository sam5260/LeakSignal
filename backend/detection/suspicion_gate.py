def evaluate_suspicion(context: dict) -> tuple[int, bool]:
    """
    Evaluates context flags to generate a temporary suspicion score.
    Returns (score, requires_deep_path).
    
    Deep path requires a COMBINATION of flags — single signals alone are normal.
    First-seen destination during business hours is common and NOT suspicious.
    Off-hours + first-seen, or off-hours + volume deviation, IS suspicious.
    """
    score = 0
    
    if context.get("is_first_seen_dest"):
        score += 10  # alone, not enough to trigger
        
    if context.get("is_rare_destination"):
        score += 8
        
    if context.get("is_off_hours"):
        score += 15  # off-hours is the strongest single signal
        
    if context.get("is_transfer_deviation"):
        score += 12  # unusual volume is suspicious
    
    # Deep path requires a meaningful combination:
    # - off_hours alone (15) is NOT enough (score < 20)
    # - off_hours + first_seen (25) IS enough
    # - off_hours + volume_deviation (27) IS enough
    # - first_seen + volume_deviation (22) IS enough (unusual volume to new dest)
    # - first_seen + rare + off_hours (33) IS very suspicious
    requires_deep_path = score >= 20
    
    return score, requires_deep_path
