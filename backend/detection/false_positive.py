def check_false_positives(event: dict) -> dict:
    """
    Checks if suspicious activity matches known legitimate patterns:
    - Approved/known destination categories
    - Internal IP ranges (10.x, 172.16-31.x, 192.168.x)
    - Cloud backup patterns
    """
    category = (event.get("destination_category") or "").lower()
    dst_ip = (event.get("dst_ip") or "").lower()

    # Category-based checks
    is_backup = "backup" in category
    is_approved = "approved" in category
    is_known = category == "known"

    # IP-based checks: internal ranges are almost always legitimate
    is_internal_ip = False
    if dst_ip:
        parts = dst_ip.split(".")
        if len(parts) == 4:
            try:
                first, second = int(parts[0]), int(parts[1])
                # 10.0.0.0/8
                if first == 10:
                    is_internal_ip = True
                # 172.16.0.0/12
                elif first == 172 and 16 <= second <= 31:
                    is_internal_ip = True
                # 192.168.0.0/16
                elif first == 192 and second == 168:
                    is_internal_ip = True
                # 127.0.0.0/8 (localhost)
                elif first == 127:
                    is_internal_ip = True
            except ValueError:
                pass

    # Known cloud provider IPs (common backup destinations)
    cloud_ips = {"52.216.146.90", "52.216.146.91", "52.216.146.92"}  # AWS S3
    is_cloud_backup = dst_ip in cloud_ips

    known_legitimate = is_backup or is_approved or is_known or is_internal_ip or is_cloud_backup

    return {
        "known_legitimate_pattern": known_legitimate,
        "reasons": {
            "backup": is_backup,
            "approved": is_approved,
            "known": is_known,
            "internal_ip": is_internal_ip,
            "cloud_backup": is_cloud_backup,
        }
    }
