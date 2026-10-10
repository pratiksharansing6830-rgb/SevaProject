# SevaProject

## Part 3 development

Apply the database migrations from the backend directory before starting the
services:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. alembic upgrade head
```

Configure `backend/.env` before starting the API. Copy `backend/.env.example`
and set `DATABASE_URL` to the deployment's database connection URL. Replace the
`SECRET_KEY` placeholder with a freshly generated secret, for example with
`python -c "import secrets; print(secrets.token_urlsafe(48))"`. The API refuses
to start with an unconfigured database URL or a missing, short, placeholder,
or obviously predictable signing key. The configuration check is not an
entropy proof: generate the key using a cryptographically secure generator and
keep the database credentials and signing key in the deployment secret store
and out of source control.

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

Continuity starts as pending or follow-up/review required. A directory listing,
contact attempt, school match, source-record status, or completed follow-up does
not confirm support. Mark a service connected or not required only after using
the continuity checklist's explicit outcome confirmation; the API records the
confirming user, time, method, and optional short non-sensitive reference.

Migration records progress from planned to active to completed. Family location
is updated only when the current migration is completed. Continuity is scoped to
the current active migration (or most recent completed migration when none is
active); unresolved needs carry forward, while connection confirmations must
be recorded again for the destination.

## Child support workflow

After signing in, create a family and add child profiles. Record each child's
education, healthcare, nutrition, protection, wellbeing, and inclusion needs,
then create a planned migration with the destination. Open the child's
continuity checklist to search nearby directory listings at the destination.
Supported destination areas use an approximate town-centre search point, and
distances are measured from that point. If the destination cannot be mapped, no
other city is substituted; enter a location on the service map instead. Search
requires authentication and sends only the location and service filters, not
child names, family identifiers, or case details. OpenStreetMap supplies the
map tiles and receives standard tile requests.

Directory results show service type, address, distance, and listed contact
details when available. A verified listing is not confirmation of suitability,
eligibility, capacity, or current availability. No matching listing does not
resolve a child's need. Use **Record contact / referral** to capture an
attempt, provider response, barrier, next step, status, and due date; edit that
record as responses arrive. Keep needs pending until the service was actually
received and explicitly confirmed in the checklist. Follow-up completion alone
does not resolve a need.

## Government planning dashboard

Government and administrator accounts can open the authorized aggregate
dashboard at `/government/dashboard`. It reports profile and migration counts,
unresolved continuity needs, follow-up workload, privacy-suppressed destination
gaps, and recent migration trends. Counts describe records in the platform, not
verified service impact. Geographic/category groups with fewer than five
children and monthly trends with fewer than five families are omitted. Seeded
demo family records marked with a `DEMO-` reference are excluded from these
indicators. The endpoint returns aggregate values only and never child or family
records.

An optional fictional demo family can be added after creating a citizen account
and applying migrations:

```bash
PYTHONPATH=. python -m scripts.seed_demo
```

The seed is labeled `DEMO DATA` and reuses the first active citizen account as
its guardian; it does not create or print credentials.