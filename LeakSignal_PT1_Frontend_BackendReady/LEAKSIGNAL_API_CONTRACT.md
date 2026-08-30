# LeakSignal PT1 API Contract

Base URL (local): `http://127.0.0.1:8000`

The frontend accepts either the snake_case examples below or the equivalent camelCase fields.

## POST `/api/upload`

Request: `multipart/form-data` with field `file`.

Example response:

```json
{
  "status": "success",
  "message": "Dataset uploaded successfully"
}
```

## GET `/api/dashboard`

```json
{
  "monitored_hosts": 24,
  "critical_hosts": 1,
  "suspicious_hosts": 2,
  "alerts_today": 4
}
```

## GET `/api/hosts`

```json
[
  {
    "host_id": "FIN-PC-07",
    "ers": 91,
    "classification": "Possible Slow Data Exfiltration",
    "last_seen": "2 min ago",
    "department": "Finance"
  }
]
```

## GET `/api/hosts/{id}`

```json
{
  "host_id": "FIN-PC-07",
  "ers": 91,
  "classification": "Possible Slow Data Exfiltration",
  "classification_label": "Possible Slow Data Exfiltration",
  "department": "Finance",
  "last_seen": "2 min ago",
  "baseline_outbound_mb": 40,
  "current_outbound_mb": 106,
  "deviation_pct": 165,
  "new_destination": "185.44.22.91",
  "destination_status": "first-seen",
  "repeated_nights": 4,
  "outbound_comparison": [
    { "label": "Day 1", "baseline_mb": 5, "current_mb": 6 },
    { "label": "Day 2", "baseline_mb": 5, "current_mb": 8 }
  ]
}
```

## GET `/api/hosts/{id}/timeline`

```json
[
  { "day": "Day 1", "date": "Aug 27", "ers": 31, "classification": "Monitor" },
  { "day": "Day 2", "date": "Aug 28", "ers": 48, "classification": "Monitor" },
  { "day": "Day 3", "date": "Aug 29", "ers": 69, "classification": "Suspicious" },
  { "day": "Day 4", "date": "Aug 30", "ers": 91, "classification": "Possible Slow Data Exfiltration" }
]
```

## GET `/api/alerts`

```json
[
  {
    "alert_id": "ALRT-1042",
    "host_id": "FIN-PC-07",
    "classification": "Possible Slow Data Exfiltration",
    "ers": 91,
    "created_at": "Aug 30, 02:47",
    "summary": "Repeated off-hours transfer pattern"
  }
]
```

## GET `/api/alerts/{id}`

```json
{
  "alert_id": "ALRT-1042",
  "host_id": "FIN-PC-07",
  "classification": "Possible Slow Data Exfiltration",
  "ers": 91,
  "created_at": "Aug 30, 02:47",
  "signals": [
    {
      "id": "sig-1",
      "name": "First-seen destination",
      "description": "Destination has not appeared in the host profile before.",
      "severity": "high"
    },
    {
      "id": "sig-2",
      "name": "Off-hours transfer",
      "description": "Transfer occurred outside the host's normal active hours.",
      "severity": "high"
    },
    {
      "id": "sig-3",
      "name": "Repeated sessions",
      "description": "Similar low-volume outbound sessions repeated across multiple nights.",
      "severity": "critical"
    },
    {
      "id": "sig-4",
      "name": "Multi-day persistence",
      "description": "The pattern persisted long enough to indicate a slow-drip behavior.",
      "severity": "critical"
    }
  ],
  "false_positive_check": {
    "approved_destination": false,
    "scheduled_backup": false,
    "result": "No legitimate explanation found"
  }
}
```

## Integration rules

1. Backend owns ERS and the final host classification.
2. Frontend only normalizes field names and displays the result.
3. Use stable `host_id`; do not use IP as permanent host identity.
4. CSV upload must stay `multipart/form-data`; do not force `Content-Type: application/json`.
5. During integration set `NEXT_PUBLIC_USE_MOCKS=false` so backend errors are not hidden by demo data.
