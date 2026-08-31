# MediKiosk — AI-Powered Clinical Intake Platform

Touchscreen kiosk for patient intake: mobile-number identification, webcam face verification (InsightFace ArcFace), an adaptive AI clinical interview (OpenAI via LangChain), and a structured case summary for the doctor.

**Stack:** FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 16 · React 19 · TypeScript · Vite · Tailwind v4 · Zustand

---

## Prerequisites

- Python 3.11–3.14
- Node.js 18+ with npm
- PostgreSQL 16 (Docker recommended)
- Webcam (for face enrollment/verification)
- OpenAI API key (optional — without it the interview uses the deterministic engine)

---

## 1. Clone

```bash
git clone https://github.com/kshxaib/MediKiosk.git
```

## 2. Start PostgreSQL

From the project root:

```bash
docker compose up -d
```

Runs Postgres 16 on `localhost:5432` (user/password/db all `medikiosk`).

<details>
<summary>Using a local PostgreSQL instead</summary>

```sql
CREATE USER medikiosk WITH PASSWORD 'medikiosk';
CREATE DATABASE medikiosk OWNER medikiosk;
```
</details>

## 3. Backend

```bash
cd backend
python -m venv .venv
```

Activate it — **`.venv`, not `venv`** (`venv/` holds only the Graphify tool):

| Shell | Command |
|---|---|
| PowerShell | `.\.venv\Scripts\Activate.ps1` |
| CMD | `.\.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `backend/.env` (copy `.env.example` and add your key):

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+psycopg://medikiosk:medikiosk@localhost:5432/medikiosk
BACKEND_CORS_ORIGINS=http://localhost:5173

JWT_SECRET_KEY=dev_insecure_jwt_secret_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

FACE_MODEL_NAME=buffalo_l
FACE_SIMILARITY_THRESHOLD=0.50
FACE_DETECTION_SIZE=640

OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
LLM_TIMEOUT_SECONDS=15.0
LLM_MAX_RETRIES=2
```

Get a key at [platform.openai.com](https://platform.openai.com/api-keys). Leave `OPENAI_API_KEY` empty to run without AI — the kiosk stays fully functional on the deterministic question engine. Settings are cached at startup, so **restart the server after editing `.env`**.

Migrate, seed, run:

```bash
alembic upgrade head
```
```bash
python -m app.db.seed
```
```bash
python -m uvicorn app.main:app --reload --port 8000
```

API at `http://localhost:8000/api/v1` · Swagger at `http://localhost:8000/docs`

> First request takes ~25s while the InsightFace models load.

## 4. Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

App at `http://localhost:5173`.

The API URL defaults to `http://localhost:8000`. To point elsewhere, create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Vite reads env files only at startup — restart `npm run dev` after changing it.

---

## Patient flow

Language → Mobile → Register (if new) → Face → Consent → Stream → Department → AI Interview → Completion

Staff/admin pages live at `/login` and `/system`.

---

## Tests & validation

```bash
cd backend && pytest
```
130 tests, all mocked — no network calls.

```bash
pytest tests/test_llm_smoke.py -v -s
```
Live OpenAI smoke test. Skipped without `OPENAI_API_KEY`; **fails** if the API call fails.

```bash
cd frontend && npm run lint && npm run build
```

---

## Troubleshooting

**`No module named uvicorn`** — the wrong venv is active. Activate `backend/.venv`, not `backend/venv`.

**Frontend shows "Network Error"** — the API port doesn't match. Backend must be on 8000, or `frontend/.env.local` must point at wherever it is. Restart `npm run dev` after editing.

**Camera blocked** — allow camera access for `http://localhost:5173` in the browser address bar.

**OpenAI 429 / offline** — expected and handled. The interview falls back to database-backed clinical questions and the case summary falls back to a deterministic narrative.

---

**Safety:** MediKiosk collects and organises clinical information only. It does not diagnose, prescribe, or recommend treatment. The doctor remains the decision-maker.
