from datetime import datetime
from typing import Dict, Any, Optional

def validate_and_normalize(row: dict) -> Optional[Dict[str, Any]]:
    """
    Validates a raw CSV row and normalizes its fields.
    Returns the normalized dictionary, or None if invalid.
    """
    try:
        # Check required fields
        required_keys = ['timestamp', 'host_id', 'dst_ip', 'bytes_sent']
        if not all(k in row and row[k] for k in required_keys):
            return None
            
        # Parse timestamp
        try:
            ts = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
            
        # Validate bytes_sent
        try:
            bytes_sent = int(row['bytes_sent'])
            if bytes_sent < 0:
                return None
        except ValueError:
            return None
            
        # Normalize protocol
        protocol = str(row.get('protocol', 'UNKNOWN')).upper()
        
        # Parse duration
        duration = int(row.get('duration', 0)) if row.get('duration', '').isdigit() else 0
        
        return {
            'timestamp': ts,
            'host_id': str(row['host_id']).strip(),
            'src_ip': str(row.get('src_ip', '')).strip(),
            'dst_ip': str(row['dst_ip']).strip(),
            'dst_port': str(row.get('dst_port', '')).strip(),
            'protocol': protocol,
            'bytes_sent': bytes_sent,
            'duration': duration,
            'destination_category': str(row.get('destination_category', 'unknown')).strip()
        }
    except Exception:
        return None
