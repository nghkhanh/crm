# Facebook Ads Agency CRM

Monorepo for a CRM built with FastAPI, Next.js 14, PostgreSQL, Redis, and APScheduler.

Enterprise rollout plan: [PRODUCT_ROADMAP.md](/Users/khanhnh/crm/PRODUCT_ROADMAP.md)
Production deploy: [DEPLOY_PRODUCTION.md](/Users/khanhnh/crm/DEPLOY_PRODUCTION.md)

## Services

- `backend`: FastAPI API, auth, jobs, integrations
- `frontend`: Next.js App Router admin UI
- `postgres`: primary database
- `redis`: optional cache/rate-limit store

## Quick start

1. Copy `.env.example` to `.env`
2. Run `docker compose up --build`
3. Open `http://localhost:3000`
4. API docs: `http://localhost:8000/docs`

## Backend dependency management

The backend now uses `uv`, [backend/pyproject.toml](/Users/khanhnh/crm/backend/pyproject.toml), and a committed [backend/uv.lock](/Users/khanhnh/crm/backend/uv.lock) instead of `requirements.txt`.

Local backend setup:

```bash
cd backend
uv sync --all-groups
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

## Operational checks

- Liveness: `http://localhost:8000/health`
- Readiness: `http://localhost:8000/api/ops/ready`
- Docker services now include healthchecks and `restart: unless-stopped`

## Lark interactive ticket flow

- Set `LARK_WEBHOOK_URL`
- Set `BACKEND_PUBLIC_BASE_URL` so Lark action buttons can call back into CRM
- Set `FRONTEND_PUBLIC_BASE_URL` so the `Xem Chi Tiet` button can open the CRM UI
- Tickets pushed to Lark now use an interactive card with:
  - `Xem Chi Tiet`
  - `Da tiep nhan`
  - `Hoan Thanh`

Note: this implementation works with the current Custom Bot webhook flow by using signed action links. If you later need actor identity from Lark or in-place card updates after click, move to a full Lark App Bot with card action callbacks.

## Backend tests

Run the backend suite inside Docker:

```bash
docker compose run --rm backend pytest tests -q
```

Or locally with `uv`:

```bash
cd backend
uv run pytest tests -q
```

## Security hardening now present

- Login lockout after repeated failed attempts
- Rate limiting for auth and webhook endpoints
- User self-service password change
- Admin password reset endpoint

## Default admin

Set `DEFAULT_ADMIN_EMAIL` and `DEFAULT_ADMIN_PASSWORD` in `.env`. The backend seeds this user on startup if it does not exist.

Default local login in this scaffold:

- Email: `nghkhanh203@gmail.com`
- Password: `changeme123`

## Demo data

Demo seed is disabled by default. Set `SEED_DEMO_DATA=true` if you explicitly want sample customers, ad accounts, transactions, invoices, tickets, and referrals on an empty database.
