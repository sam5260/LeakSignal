def calculate_ers(signals: dict) -> tuple[int, str]:
    """
    Calculates Exfiltration Risk Score (ERS) and determines the final classification band.
    signals is a dictionary of boolean flags.
    """
    score = 0
    
    # Base risk weights
    if signals.get("new_destination"):
        score += 15
    if signals.get("rare_destination"):
        score += 10
    if signals.get("off_hours"):
        score += 15
    if signals.get("volume_deviation"):
        score += 10
    if signals.get("repeated_transfers"):
        score += 15
    if signals.get("multi_day_persistence"):
        score += 20
    if signals.get("ml_anomaly"):
        score += 10
        
    # False positive downgrades
    if signals.get("known_legitimate_pattern"):
        score -= 20
        
    # Normalize 0-100
    score = max(0, min(100, score))
    
    # Classification bands
    if score <= 29:
        classification = "Normal"
    elif score <= 49:
        classification = "Monitor"
    elif score <= 74:
        classification = "Suspicious"
    else:
        classification = "Possible Slow Data Exfiltration"
        
    return score, classification
