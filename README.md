# Social Intent Miner

A SaaS platform that monitors Reddit for high-intent leads relevant to your business. It scores posts for buying/need signals and organizes them into a pipeline you can act on.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────┐
│  Next.js     │────▶│  FastAPI      │────▶│ Postgres │
│  Frontend    │     │  Backend      │     │          │
└─────────────┘     └──────┬───────┘     └──────────┘
                           │
                    ┌──────▼───────┐     ┌──────────┐
                    │  Redis Queue  │────▶│  Worker  │
                    └──────────────┘     └──────────┘
```

**Stack:** FastAPI, PostgreSQL, Redis, Next.js, Stripe, SQLAlchemy

## Features

- **Multi-tenant** — Organizations with member accounts
- **Project-based lead mining** — Define keywords and target subreddits
- **Intent scoring** — Weighted NLP scoring with 30+ intent signals
- **Lead pipeline** — Status tracking (new → contacted → qualified → converted)
- **Background scraping** — Redis-based worker processes scrape jobs
- **Stripe billing** — Free/Pro plans with checkout, webhooks, and customer portal
- **Secure auth** — bcrypt password hashing, JWT tokens, no hardcoded secrets

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env — set JWT_SECRET, DB_PASSWORD, and API keys
```

### 2. Generate a JWT secret

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Start all services

```bash
docker compose up --build
```

Services:
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs (debug mode only)

### 4. Set up Stripe (optional)

1. Create products/prices in Stripe Dashboard
2. Add `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, and price IDs to `.env`
3. Set up webhook endpoint: `https://yourdomain.com/api/v1/billing/webhook`

### 5. Set up Reddit API (recommended)

1. Create an app at https://www.reddit.com/prefs/apps
2. Add `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` to `.env`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create account + org |
| POST | `/api/v1/auth/login` | Get JWT token |
| GET | `/api/v1/auth/me` | Current user profile |
| GET | `/api/v1/projects` | List projects |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects/:id` | Get project |
| PATCH | `/api/v1/projects/:id` | Update project |
| DELETE | `/api/v1/projects/:id` | Delete project |
| GET | `/api/v1/leads/:projectId` | List leads (paginated) |
| PATCH | `/api/v1/leads/:projectId/leads/:leadId` | Update lead status |
| GET | `/api/v1/leads/:projectId/stats` | Lead statistics |
| GET | `/api/v1/billing/subscription` | Current plan |
| POST | `/api/v1/billing/checkout` | Stripe checkout |
| POST | `/api/v1/billing/portal` | Stripe billing portal |
| GET | `/health` | Health check |

## Project Structure

```
backend/
  main.py           # FastAPI app with CORS, logging, error handling
  config.py         # Pydantic Settings (env-based config)
  database.py       # Async SQLAlchemy engine + session
  models.py         # User, Organization, Project, Lead models
  schemas.py        # Pydantic request/response schemas
  routes/
    auth.py         # Register, login, JWT, get_current_user dependency
    projects.py     # CRUD for projects with plan limit enforcement
    leads.py        # Paginated leads, status updates, stats
    billing.py      # Stripe checkout, webhooks, portal
    health.py       # Health/readiness checks
  services/
    nlp.py          # Weighted intent scoring (30+ signals)
    reddit.py       # Reddit OAuth + search with error handling

frontend/
  pages/
    _app.js         # Auth provider + layout wrapper
    index.js        # Redirect to dashboard/login
    login.js        # Login form
    register.js     # Registration form
    dashboard.js    # Project list + create
    billing.js      # Subscription management
    projects/[id].js # Project detail with lead table
  components/
    Layout.js       # Nav bar + auth guard
    LeadTable.js    # Sortable lead table with status management
  lib/
    api.js          # API client with auth headers
    auth.js         # Auth context + hooks

worker/
  worker.py         # Redis queue consumer, scraping + scoring pipeline
```

## Security Checklist

- [x] JWT secret from environment variable (no hardcoded secrets)
- [x] bcrypt password hashing
- [x] CORS restricted to allowed origins
- [x] Input validation via Pydantic schemas
- [x] SQL injection prevention via SQLAlchemy ORM
- [x] URL parameter encoding (no SSRF in Reddit service)
- [x] Stripe webhook signature verification
- [x] Multi-tenant data isolation (organization-scoped queries)
- [x] Global exception handler (no stack traces to client)
- [x] Swagger docs disabled in production
