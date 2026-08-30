# LeakSignal PT1 Frontend — Fixed Backend-Ready Build

Frontend-only Next.js dashboard for LeakSignal Prototype 1.

## Run locally

```bash
npm install
copy .env.example .env.local
npm run dev
```

On macOS/Linux use:

```bash
cp .env.example .env.local
```

Open `http://localhost:3000`.

## Backend integration

Expected FastAPI base URL in `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_USE_MOCKS=false
```

Supported PT1 API contract:

- `POST /api/upload`
- `GET /api/dashboard`
- `GET /api/hosts`
- `GET /api/hosts/{id}`
- `GET /api/hosts/{id}/timeline`
- `GET /api/alerts`
- `GET /api/alerts/{id}`

The API adapter accepts both snake_case FastAPI JSON and the frontend's camelCase model. Classification is expected to come from the backend; the frontend only normalizes it for display.

## What was fixed

- Added `/api` prefixes to all backend routes.
- Fixed multipart CSV upload headers (no forced JSON content type).
- Made mock fallback environment-controlled.
- Removed dependency on non-contract dashboard endpoints: risk distribution is derived from `/api/hosts`, and ERS activity uses `/api/hosts/FIN-PC-07/timeline`.
- Added response adapters for common FastAPI snake_case fields.
- Added complete Next.js/Tailwind/TypeScript project configuration missing from the source archive.
- Added missing `clsx` dependency used by `lib/utils.ts`.

## Recommended integration mode

While connecting the backend, set:

```env
NEXT_PUBLIC_USE_MOCKS=false
```

That prevents a failed backend request from silently displaying demo data.


## Backend-ready defaults

This package is configured for real FastAPI integration by default:

- API routes use the `/api/...` contract.
- `NEXT_PUBLIC_USE_MOCKS=false` is the recommended integration setting.
- CSV upload sends `FormData` without forcing an `application/json` Content-Type.
- ERS classification is owned by the backend. The frontend does not infer a verdict from the ERS score.
- Missing or invalid backend classifications fail visibly during integration instead of silently becoming `normal`.

For UI-only demo mode, explicitly set `NEXT_PUBLIC_USE_MOCKS=true`.
