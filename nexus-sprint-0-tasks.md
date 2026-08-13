# Sprint 0 — Groundwork: Tasks, Deliverables & Learning

**Companion:** `nexus-action-plan.md` (Sprint 0 section — this doc expands it with deliverables + learning goals)

**Goal of this sprint:** no game logic yet. Just prove you have a working skeleton — repo, local infra, config, and one real endpoint that talks to both Postgres and Redis — before writing a single line of the actual app.

---

## 1. Repo & tooling

**Tasks**
- [✅] Create GitHub repo `nexus` (private), clone locally
- [✅] `README.md` — one paragraph: what Nexus is, stack, how to run
- [✅] `.gitignore` (Python + node + `.env`)
- [✅] Deps declared in `pyproject.toml` (matches committed `uv.lock`) — `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `asyncpg`, `pydantic-settings`, `redis`, `pytest`, `httpx`, `ruff`. `sqlmodel`/`alembic` deferred to Sprint 1. ⚠️ `uv` not installed on this machine yet — run `uv sync` once it is.
- [✅] `ruff.toml` + `ruff check .` passes
- [✅] Folder skeleton (`app/`, `tests/`, `docs/`, `docker-compose.yml`) — `alembic/`/`Dockerfile` deferred to Sprint 1/3

**Deliverable:** a pushed repo with a clean folder structure, dependencies installed, and linting wired up — nothing runs yet, but the scaffolding is real.

**You'll learn**
- Modern Python dependency management (`uv`/`poetry`) vs `pip freeze` chaos
- Why FastAPI apps are laid out as `models/ routers/ engine/ services/` (separation of pure logic from HTTP/DB concerns — this split pays off hugely by Sprint 2)
- `ruff` as a fast, all-in-one linter/formatter replacing flake8+black+isort

---

## 2. The one decision that matters (ADR)

**Tasks**
- [✅] Write `docs/adr-001-database.md` documenting the Neon + R2 decision, dated, with a 5-line rationale
- [✅] Note the downstream consequence: this decides how Sprint 5 (auth) and Sprint 7 (photos) get built

**Deliverable:** a short, permanent Architecture Decision Record — the kind of artifact real engineering teams keep so decisions aren't re-litigated every few weeks.

**You'll learn**
- What an ADR is and why writing one (even solo) forces you to actually justify a choice instead of drifting
- The tradeoff between managed all-in-one platforms (Supabase-style) vs composing best-of-breed services yourself (Neon for Postgres, R2 for storage, `fastapi-users` for auth)

---

## 3. Local infra (Docker)

**Tasks**
- [✅] `docker-compose.yml` with `postgres:16` + `redis:7`, volumes + exposed ports
- [ ] `docker compose up -d` → confirm both containers healthy — **⚠️ Docker Desktop not installed on this machine, do this step yourself**
- [✅] `app/config.py` using `pydantic-settings` to read `DATABASE_URL` / `REDIS_URL` from `.env`
- [✅] `.env.example` committed; real `.env` gitignored

**Deliverable:** `docker compose up -d` brings up a local Postgres + Redis you can connect to, with config loaded via environment variables (not hardcoded).

**You'll learn**
- Docker Compose basics: services, volumes, port mapping, healthchecks
- Why you develop against the *same* engine (Postgres) you'll run in prod, instead of SQLite locally
- 12-factor config: settings come from the environment, secrets never get committed
- `pydantic-settings` for typed, validated config objects instead of raw `os.environ` calls

---

## 4. Prove it runs (first endpoint)

**Tasks**
- [✅] `app/main.py` — FastAPI app + `GET /health` that does a **real** DB ping and Redis ping, not just a static response
- [✅] `tests/test_health.py` — `httpx` test hitting `/` and `/health`
- [✅] `pytest` green (2 passed — verified via throwaway pip venv, `uv` not installed here)

**Deliverable:** hitting `curl localhost:8000/health` returns `{"status":"ok","db":"ok","redis":"ok"}` — proof the whole chain (app → config → Postgres, app → config → Redis) actually works end to end.

**You'll learn**
- FastAPI basics: app instance, route handlers, async endpoints
- Writing a *meaningful* healthcheck (one that exercises real dependencies) vs a fake one that always says "ok"
- Async DB/cache clients (`asyncpg`, `redis.asyncio`) and why FastAPI apps are built async-first
- API testing with `httpx` + `pytest` — your first automated test, however small

---

## ✅ Sprint exit test

```
docker compose up -d && uvicorn app.main:app --reload
curl localhost:8000/health
# → {"status":"ok","db":"ok","redis":"ok"}
```

If this passes, Sprint 0 is done — you have a real, runnable, tested skeleton to build the game on.

**Status (2026-08-13):** All code/config is written and verified against a throwaway pip venv — `pytest` (2 passed) and `ruff check .` (all checks passed) are green, and `/health` correctly returns `{"status":"degraded","db":"error: ConnectionRefusedError","redis":"error: ConnectionError"}` when Postgres/Redis aren't reachable. **Remaining before this is truly done:** install Docker Desktop (and `uv`, to match the project's chosen tooling) on this machine, run `docker compose up -d`, then re-run the exit test to see `"ok"/"ok"/"ok"`.

> ⚠️ **Timebox tooling to 1 session.** If you're 90 minutes into debating `uv` vs `poetry`, you've already lost. Pick and move.

---

## Summary: what you walk away with

| Area | Deliverable | Core skill gained |
|---|---|---|
| Repo | Pushed GitHub repo, linted, structured | Project scaffolding, tooling hygiene |
| Decision-making | `adr-001-database.md` | Writing durable technical decisions |
| Infra | Working `docker-compose.yml` | Containerized local dev environments |
| Config | `config.py` via pydantic-settings | 12-factor config, secret management |
| API | Live `/health` endpoint + passing test | FastAPI, async I/O, integration testing |

*Once this is ticked, move to Sprint 1 (Data foundation) in `nexus-action-plan.md`.*
