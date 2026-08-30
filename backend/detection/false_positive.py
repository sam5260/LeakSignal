def check_false_positives(event: dict) -> dict:
    """
    Checks if suspicious activity matches known legitimate automation or backups.
    """
    category = event.get("destination_category", "").lower()
    
    is_backup = "backup" in category
    is_approved = "approved" in category
    
    return {
        "known_legitimate_pattern": is_backup or is_approved
    }
