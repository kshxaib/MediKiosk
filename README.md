# MediKiosk

An AI-powered, multilingual clinical case-taking and patient-intake platform.

> **Status: Phase 1 — Foundation.** This repository currently contains only the
> project foundation: a runnable backend service, database plumbing, and a
> frontend scaffold. There is **no clinical functionality yet** — patient
> intake, authentication, AI, speech, and document features arrive in later
> phases. See [`PROJECT_REQUIREMENT.md`](PROJECT_REQUIREMENT.md) for the full
> specification and phase plan.

## Tech stack

| Layer     | Technology                                                        |
| --------- | ----------------------------------------------------------------- |
| Backend   | Python · FastAPI · Pydantic Settings · SQLAlchemy 2 · Alembic     |
| Database  | PostgreSQL 16 (via Docker) · psycopg 3 driver                     |
| Frontend  | React 19 · TypeScript · Vite · Tailwind CSS v4 · React Router v7  |

## Repository layout

```
MediKiosk/
├── backend/            FastAPI application
│   ├── app/            application package (config, db, api, services, schemas)
│   ├── alembic/        database migrations (empty baseline in Phase 1)
│   ├── tests/          pytest suite
│   └── requirements.txt
├── frontend/           React + TypeScript kiosk client
│   └── src/            pages, components, services, hooks
├── docker-compose.yml  local PostgreSQL
└── PROJECT_REQUIREMENT.md
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (for PostgreSQL)

## Getting started

### 1. Start PostgreSQL

```bash
docker compose up -d db
```

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # adjust if needed
alembic upgrade head          # applies the empty baseline migration
uvicorn app.main:app --reload --port 8000
```

Verify the service:

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/config/public
```

Interactive API docs are served at http://localhost:8000/docs.

Run the backend tests:

```bash
cd backend
pytest
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env          # sets VITE_API_BASE_URL
npm run dev
```

Open http://localhost:5173. The `/system` route is a **developer** status page
that reports backend and database connectivity — it is not a clinical screen.

## Configuration & secrets

- Backend configuration lives in `backend/.env` (see `backend/.env.example`).
- Frontend configuration lives in `frontend/.env` (see `frontend/.env.example`);
  only `VITE_`-prefixed values are exposed to the browser, so **no backend
  secret may ever be placed there**.
- `.env` files are gitignored and must never be committed. Only `.env.example`
  templates are tracked.

## API (Phase 1)

| Method | Path                    | Description                                  |
| ------ | ----------------------- | -------------------------------------------- |
| GET    | `/api/v1/health`        | Liveness + real PostgreSQL check (503 if down) |
| GET    | `/api/v1/config/public` | Non-secret public configuration              |

## What's next

Phase 2 introduces staff authentication (the first real database models,
password hashing, login, JWT, and role-based access control). No Phase 2+ code
exists in this repository yet.
