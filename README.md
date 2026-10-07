# SevaProject

## Part 3 development

Apply the database migrations from the backend directory:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. uvicorn app.main:app --reload
```

FastAPI documents the API at `/docs` and `/redoc`. The family, child, migration,
service continuity, and follow-up routes require a valid Part 2 JWT.

An optional fictional demo family can be added after creating a citizen account
and applying migrations:

```bash
PYTHONPATH=. python -m scripts.seed_demo
```

The seed is labeled `DEMO DATA` and reuses the first active citizen account as
its guardian; it does not create or print credentials.