# SevaProject

## Part 3 development

Apply the database migrations from the backend directory before starting the
services:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. alembic upgrade head
```

Start the API and frontend in separate terminals from the repository root:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

```bash
npm run dev -- --host 0.0.0.0
```

The frontend calls `/api/v1` on its own origin. Vite proxies those requests to
the API on port `8001`, which also works when the frontend is opened through a
Codespaces forwarded port.

FastAPI documents the API at `/docs` and `/redoc`. The family, child, migration,
service continuity, and follow-up routes require a valid Part 2 JWT.

An optional fictional demo family can be added after creating a citizen account
and applying migrations:

```bash
PYTHONPATH=. python -m scripts.seed_demo
```

The seed is labeled `DEMO DATA` and reuses the first active citizen account as
its guardian; it does not create or print credentials.