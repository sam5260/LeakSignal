def calculate_ers(signals: dict) -> tuple[int, str]:
    """
    Calculates Exfiltration Risk Score (ERS, 0-100) and classification band.

    Target scores for demo scenario:
    - FIN-PC-07: ~91 (slow exfil to external IP, off-hours, persistent across days)
    - HR-PC-02: ~65 (single large off-hours transfer to external IP)
    - BACKUP-SERVER-01: 9 (legitimate backup → override)
    - DEV-PC-01: 9 (all normal traffic → override)

    Weight design:
    HR needs 65 from 4 signals: new_dest + off_hours + volume_dev + external
    FIN needs 91 from 8 signals: HR's 4 + repeated + persistence + correlation + growing
    Difference (26 points) comes from: repeated(8) + persistence(10) + correlation(5) + growing(3)
    """
    # --- Known legitimate pattern: override immediately ---
    if signals.get("known_legitimate_pattern"):
        return 9, "Normal"

    score = 0

    # --- Core risk signals ---
    if signals.get("new_destination"):
        score += 12     # External/unknown destination (first-seen)
    if signals.get("rare_destination"):
        score += 8      # Rare but not first-seen
    if signals.get("off_hours"):
        score += 20     # Strongest single signal — activity when no one is there
    if signals.get("volume_deviation"):
        score += 18     # Unusually large transfer (3σ+ above baseline)
    if signals.get("external_destination"):
        score += 15     # External IP significantly more suspicious than internal
    if signals.get("repeated_transfers"):
        score += 8      # Same suspicious pattern repeated (adds consistency)
    if signals.get("multi_day_persistence"):
        score += 10     # Pattern persists across multiple days
    if signals.get("temporal_correlation"):
        score += 5      # Consistent timing suggests automation
    if signals.get("growing_volume"):
        score += 3      # Slight escalation over time

    # --- Normalize 0-100 ---
    score = max(0, min(100, score))

    # --- Classification bands ---
    if score <= 29:
        classification = "Normal"
    elif score <= 49:
        classification = "Monitor"
    elif score <= 74:
        classification = "Suspicious"
    else:
        classification = "Possible Slow Data Exfiltration"

    return score, classification
