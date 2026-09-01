# LeakSignal

**Slow Data Exfiltration Detection for Enterprise Networks**

LeakSignal is a network security monitoring tool that detects low-and-slow data exfiltration — the kind of attacks that traditional firewalls and DLP systems miss. It ingests CSV network traffic logs, builds per-host behavioral baselines, and assigns an **Exfiltration Risk Score (ERS)** to every monitored host using a multi-stage detection pipeline.

---

## Live Demo

| Component | URL |
|-----------|-----|
| **Frontend** (Next.js) | [https://leaksignal-ochre.vercel.app](https://leaksignal-ochre.vercel.app) |
| **Backend API** (FastAPI) | [https://leaksignal.onrender.com](https://leaksignal.onrender.com) |

> **Note:** The backend runs on Render's free tier. The first request after idle may take 30–50 seconds to wake up.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      FRONTEND                            │
│              Next.js 16 + Tailwind + Recharts            │
│         Dashboard · Hosts · Alerts · Upload UI           │
└──────────────────────┬───────────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────▼───────────────────────────────────┐
│                      BACKEND                             │
│              FastAPI + SQLAlchemy + SQLite                │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  CSV Upload  │  │   Baseline   │  │   Detection    │  │
│  │  & Parsing   │  │   Engine     │  │   Engine       │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                │                   │           │
│         └────────┬───────┘                   │           │
│                  ▼                           │           │
│         ┌──────────────┐                    │           │
│         │  Host Profile │◄──────────────────┘           │
│         │  & Baseline   │                               │
│         └──────┬───────┘                               │
│                ▼                                        │
│         ┌──────────────┐                               │
│         │  ERS Engine   │──► Alerts · History · API     │
│         └──────────────┘                               │
└──────────────────────────────────────────────────────────┘
```

---

## Detection Pipeline

When a CSV is uploaded, each network event flows through a **three-stage pipeline**:

### Stage 1 — Quick Context Checks

Fast-path analysis against the host's existing baseline:

| Check | Logic |
|-------|-------|
| **Off-hours activity** | Hour has < 5% of peak activity |
| **First-seen destination** | Destination not in host's known destinations |
| **Rare destination** | Destination exists but count ≤ 1 |
| **Volume deviation** | Transfer > 3σ above mean (or 5× if no variance data) |
| **External destination** | IP is not in RFC 1918 private ranges |

### Stage 2 — Suspicion Gate

Combines quick-check flags into a suspicion score. **Requires a combination of signals** — a single flag alone does not trigger escalation:

| Threshold | Action |
|-----------|--------|
| Score < 20 | Fast path — normal event, update baseline |
| Score ≥ 20 | Deep path — suspicious, triggers full analysis |

### Stage 3 — Deep Analysis

For suspicious events, the engine runs:

- **Historical context gathering** — fetches past events for the same host+destination
- **Repetition analysis** — checks for 3+ similar events
- **Persistence analysis** — checks for multi-day patterns
- **Temporal correlation** — hour consistency, volume trends, correlation strength
- **False positive filtering** — suppresses alerts for known legitimate patterns (approved destinations, cloud backups, internal IPs)

### ERS Scoring

The final **Exfiltration Risk Score (ERS)** is calculated from weighted signals:

| Signal | Points |
|--------|--------|
| Off-hours activity | +20 |
| Volume deviation (3σ+) | +18 |
| External destination | +15 |
| First-seen destination | +12 |
| Multi-day persistence | +10 |
| Repeated transfers | +8 |
| Rare destination | +8 |
| Temporal correlation | +5 |
| Growing volume | +3 |
| **Known legitimate pattern** | **Override → 9 (Normal)** |

**Classification bands:**

| ERS Range | Classification |
|-----------|---------------|
| 0–29 | Normal |
| 30–49 | Monitor |
| 50–74 | Suspicious |
| 75–100 | Possible Slow Data Exfiltration |

---

## Expected Demo Results

After uploading `dataset.csv` (763 events, 4 hosts, 7 days):

| Host | ERS | Classification | Signals |
|------|-----|---------------|---------|
| **FIN-PC-07** | **91** | Possible Slow Data Exfiltration | Off-hours + first-seen destination + external IP + repeated sessions + multi-day persistence + temporal correlation |
| **HR-PC-02** | **73** | Suspicious | Off-hours + first-seen destination + external IP + volume deviation |
| **BACKUP-SERVER-01** | **9** | Normal | Known backup destination → false positive override |
| **DEV-PC-01** | **9** | Normal | All traffic within baseline |

FIN-PC-07's timeline shows escalation: `9 → 9 → 65 → 75 → 88 → 91` over 7 days.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 18, TypeScript, Tailwind CSS, Recharts |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, SQLite |
| **Detection Engine** | Custom multi-stage pipeline with Welford's online variance |
| **Hosting** | Vercel (frontend), Render (backend) |

---

## Project Structure

```
LeakSignal/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── database.py             # SQLAlchemy models & schema
│   ├── api/
│   │   ├── upload.py           # CSV upload + detection pipeline
│   │   ├── dashboard.py        # Dashboard summary + charts
│   │   ├── hosts.py            # Host list + detail + timeline
│   │   └── alerts.py           # Alerts list + detail + reset
│   ├── risk/
│   │   └── ers.py              # ERS calculation engine
│   ├── detection/
│   │   ├── quick_checks.py     # Stage 1: baseline comparison
│   │   ├── suspicion_gate.py   # Stage 2: threshold gating
│   │   ├── deep_context.py     # Stage 3a: historical context
│   │   ├── repetition.py       # Stage 3b: repetition analysis
│   │   ├── persistence.py      # Stage 3c: multi-day persistence
│   │   ├── correlation.py      # Stage 3d: temporal correlation
│   │   └── false_positive.py   # Stage 3e: FP filtering
│   ├── baseline/
│   │   └── baseline_engine.py  # Welford's online variance tracker
│   ├── profiles/
│   │   ├── host_identity.py    # Host resolution
│   │   └── host_profile.py     # Profile management
│   ├── ingestion/
│   │   └── csv_loader.py       # CSV parsing + event streaming
│   └── demo_data/
│       ├── dataset.csv         # 763 events, 4 hosts (demo)
│       └── test_dataset.csv    # 85 events, 4 hosts (testing)
├── LeakSignal_PT1_Frontend_BackendReady/
│   ├── app/                    # Next.js App Router pages
│   │   ├── page.tsx            # Dashboard overview
│   │   ├── upload/page.tsx     # Upload interface
│   │   ├── hosts/[id]/page.tsx # Host detail view
│   │   ├── alerts/page.tsx     # Alerts list
│   │   └── alerts/[id]/page.tsx# Alert evidence
│   ├── components/             # UI components
│   ├── services/api.ts         # API client
│   ├── types/                  # TypeScript types
│   └── lib/mockData.ts         # Offline mock fallback
├── main.py                     # Root wrapper (Render auto-detect)
├── requirements.txt            # Python dependencies
└── render.yaml                 # Render deployment config
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API health check + version |
| `POST` | `/api/upload` | Upload CSV dataset for analysis |
| `GET` | `/api/dashboard` | Dashboard summary (hosts, alerts, distribution) |
| `GET` | `/api/hosts` | List all monitored hosts with ERS |
| `GET` | `/api/hosts/{id}` | Host detail + baseline metrics |
| `GET` | `/api/hosts/{id}/timeline` | ERS history for timeline chart |
| `GET` | `/api/alerts` | List all alerts |
| `GET` | `/api/alerts/{id}` | Alert detail + evidence |
| `POST` | `/api/reset` | Reset database for clean re-run |
| `POST` | `/api/reload` | Reset + reload demo dataset |

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### Backend

```bash
cd backend
pip install -r ../requirements.txt
python main.py
```

Backend runs at `http://localhost:8000`.

### Frontend

```bash
cd LeakSignal_PT1_Frontend_BackendReady
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

### Quick Test

```bash
# Upload the demo dataset
curl -X POST http://localhost:8000/api/upload \
  -F "file=@backend/demo_data/dataset.csv"

# Check results
curl http://localhost:8000/api/dashboard
curl http://localhost:8000/api/hosts
```

---

## CSV Format

The backend accepts network traffic CSVs with these columns:

| Column | Type | Description |
|--------|------|-------------|
| `host_id` | string | Unique host identifier |
| `src_ip` | string | Source IP address |
| `dst_ip` | string | Destination IP address |
| `dst_port` | string | Destination port |
| `protocol` | string | Protocol (TCP/UDP) |
| `bytes_sent` | integer | Bytes transferred |
| `bytes_received` | integer | Bytes received |
| `duration` | integer | Session duration (seconds) |
| `timestamp` | datetime | ISO 8601 timestamp |
| `destination_category` | string | Category (Approved, Known, Backup, Uncategorized) |

---

## Deployment

### Render (Backend)

The `render.yaml` at the project root configures automatic deployment:

```yaml
services:
  - type: web
    name: leaksignal
    runtime: python
    rootDir: backend
    buildCommand: pip install -r ../requirements.txt
    startCommand: python main.py
```

### Vercel (Frontend)

Deployed from `LeakSignal_PT1_Frontend_BackendReady/` with:

```json
{
  "framework": "nextjs",
  "buildCommand": "next build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
```

Environment variable: `NEXT_PUBLIC_API_BASE_URL=https://leaksignal.onrender.com`

---

## Key Design Decisions

1. **Suspicion gate requires signal combinations** — prevents false positives from single-signal triggers (e.g., one off-hours transfer alone doesn't escalate)
2. **Baseline only updates from normal events** — prevents poisoning from suspicious traffic
3. **ERS keeps highest score per host** — worst-case posture, never downgrades
4. **False positive override** — known backup destinations, approved categories, and internal IPs immediately classify as Normal (ERS = 9)
5. **Welford's online variance** — computes running mean and variance without storing all historical values

---

## License

This project was built for the **IQOO Pune Battle Hackathon**.

---

**Built by Samar Rai**
