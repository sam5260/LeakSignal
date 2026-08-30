def evaluate_suspicion(context: dict) -> tuple[int, bool]:
    """
    Evaluates context flags to generate a temporary suspicion score.
    Returns (score, requires_deep_path).
    Deep path is triggered if score >= 25.
    """
    score = 0
    
    if context.get("is_first_seen_dest"):
        score += 20
        
    if context.get("is_off_hours"):
        score += 15
        
    if context.get("is_transfer_deviation"):
        score += 15
        
    requires_deep_path = score >= 15
    return score, requires_deep_path
