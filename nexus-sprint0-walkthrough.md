# Nexus — Sprint 0: The Beginner's Walkthrough

**Goal of this week:** Get an empty-but-running web server on your own computer, talking to a database and a cache. Nothing is on the internet yet. Nothing does anything useful yet. You're just building the workbench.

**Think of it like Minecraft:** before you build anything, you punch a tree and make a crafting table. This sprint is your crafting table.

**Time:** 3–5 hours total, spread over the week. Don't rush it — this is the part that makes every later sprint easy.

**What you'll have at the end:** Type one command, open your browser, and see `{"status":"ok","db":"ok","redis":"ok"}`. That green "ok" means your server, your database, and your cache are all alive and talking. That's the whole win.

> **A note on "beginner":** you already know Node, TypeScript, Postgres and Redis. So this isn't teaching you programming — it's walking you through the *Python + FastAPI + Docker* way of doing the setup you've done before in another language. Where something has a Node equivalent, I'll point it out.

---

## Step 1 — Install your tools

You need four things. Check each with the "verify" command; if it prints a version, you're good.

### 1a. `uv` (Python package + environment manager)
This is the big one. `uv` is like `npm` for Python — it manages your packages *and* can even install Python itself, so you don't have to install Python separately.

**Mac / Linux** — paste into your terminal:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
**Windows** — paste into **PowerShell**:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Then **close and reopen your terminal**, and verify:
```bash
uv --version
```
✅ You should see something like `uv 0.5.x`. If it says "command not found," close the terminal fully and open a new one (the installer added `uv` to your PATH, but only new terminals see it).

### 1b. Git
Verify:
```bash
git --version
```
If missing: Mac → `xcode-select --install`; Windows → install from [git-scm.com](https://git-scm.com); Linux → `sudo apt install git`.

### 1c. Docker Desktop
This runs your Postgres and Redis in the background without you installing them directly. Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop), install it, then **open the Docker Desktop app and leave it running.**

Verify (the app must be open):
```bash
docker --version
docker ps
```
✅ `docker ps` should print a table header with no rows (empty is correct — nothing's running yet). If it says "Cannot connect to the Docker daemon," Docker Desktop isn't open. Open it, wait for the whale icon to go steady, try again.

### 1d. VS Code (your editor)
Download from [code.visualstudio.com](https://code.visualstudio.com). After installing, open it and install the **Python** extension (click the extensions icon on the left, search "Python", install the Microsoft one).

---

## Step 2 — Make the GitHub repo

1. Go to [github.com/new](https://github.com/new).
2. Repository name: `nexus`
3. Set it to **Private**.
4. Check **"Add a README file."**
5. Click **Create repository.**
6. On the repo page, click the green **Code** button → copy the HTTPS URL (looks like `https://github.com/yourname/nexus.git`).

Now clone it to your computer. Pick a folder you like (e.g. your projects folder) and run:
```bash
git clone https://github.com/yourname/nexus.git
cd nexus
```
✅ You're now *inside* the `nexus` folder. Everything from here happens in this folder.

Open it in VS Code:
```bash
code .
```
(The `.` means "this folder.")

---

## Step 3 — Start the Python project

Inside the `nexus` folder, run:
```bash
uv init --no-workspace
```
This creates a `pyproject.toml` (Python's version of `package.json`) and a couple of starter files. You can delete the sample file it makes:
```bash
rm hello.py   # (Windows PowerShell: del hello.py) — ignore if it doesn't exist
```

Tell `uv` which Python to use (it'll download it for you if needed):
```bash
uv python install 3.12
uv python pin 3.12
```
✅ This creates a `.python-version` file pinning Python 3.12.

---

## Step 4 — Install the packages

Run this one command:
```bash
uv add "fastapi" "uvicorn[standard]" "sqlalchemy" "asyncpg" "pydantic-settings" "redis"
```
Then the dev tools (for testing + linting):
```bash
uv add --dev "pytest" "httpx" "ruff"
```

**What each one is** (so the names aren't a mystery):
- **fastapi** — the web framework. Like Express/Fastify in Node.
- **uvicorn** — the server that actually runs FastAPI. Like `node server.js`.
- **sqlalchemy** — talks to Postgres. (We'll add the SQLModel layer on top in Sprint 1.)
- **asyncpg** — the fast async Postgres driver SQLAlchemy uses under the hood.
- **pydantic-settings** — loads config from a `.env` file, safely and typed.
- **redis** — talks to Redis.
- **pytest / httpx** — for writing and running tests.
- **ruff** — the linter/formatter. Like ESLint + Prettier in one.

✅ You now have a `uv.lock` file and a `.venv` folder. **Never edit those by hand.** `uv` manages them.

---

## Step 5 — Create the folder structure

In VS Code, create these folders and empty files. (You can also do it in the terminal — commands below.)

```
nexus/
├── app/
│   ├── __init__.py
│   ├── main.py          ← the web server
│   ├── config.py        ← reads settings from .env
│   └── db.py            ← connects to Postgres + Redis
├── tests/
│   └── test_health.py   ← our first test
├── docs/
│   └── adr-001-database.md   ← the one decision we make this sprint
├── docker-compose.yml   ← runs Postgres + Redis
├── .env                 ← your secrets (never committed)
├── .env.example         ← a template (committed, safe)
└── .gitignore
```

Terminal shortcut to make the folders/files (Mac/Linux):
```bash
mkdir -p app tests docs
touch app/__init__.py app/main.py app/config.py app/db.py \
      tests/test_health.py docs/adr-001-database.md \
      docker-compose.yml .env .env.example .gitignore
```
Windows PowerShell:
```powershell
mkdir app,tests,docs
ni app/__init__.py,app/main.py,app/config.py,app/db.py,tests/test_health.py,docs/adr-001-database.md,docker-compose.yml,.env,.env.example,.gitignore
```

> **Why `__init__.py`?** An empty file that tells Python "this folder is a package you can import from." No Node equivalent — just always put one in a folder you import from.

---

## Step 6 — Make the ONE decision (and don't stall on it)

Beginners lose weeks here. I'll make the call for you: **use Supabase.** It gives you a managed Postgres database plus login and photo storage later, all free. You can always change your mind — nothing this sprint depends on it, because you're running Postgres *locally* via Docker for now.

Paste this into `docs/adr-001-database.md`:

```markdown
# ADR-001: Database & Backend Services

**Date:** <today's date>
**Decision:** Use Supabase (managed Postgres + Auth + Storage).

**Why:** Solo beginner project. Supabase hands me login and photo storage
for free later, so I don't build those from scratch. Managed Postgres means
no database ops. Free tier is plenty for ~20 friends.

**Consequence:** Sprint 5 uses Supabase Auth. Sprint 7 uses Supabase Storage.
Locally (Sprint 0) I run Postgres in Docker; I'll point at Supabase's
Postgres when I deploy in Sprint 3.

**Revisit if:** free-tier limits hurt, or I want to self-host everything.
```

Done. Decision locked. Move on.

---

## Step 7 — Fill in the files (copy-paste each one)

### `.gitignore`
Keeps secrets and junk out of Git.
```gitignore
.venv/
__pycache__/
*.pyc
.env
.pytest_cache/
.ruff_cache/
```

### `.env` (your real settings — stays on your machine)
```env
DATABASE_URL=postgresql+asyncpg://nexus:nexus@localhost:5432/nexus
REDIS_URL=redis://localhost:6379/0
```

### `.env.example` (a safe template you *do* commit, so future-you knows what's needed)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
```

### `docker-compose.yml`
This describes the two background services. `docker compose up` reads it and starts them.
```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: nexus
      POSTGRES_PASSWORD: nexus
      POSTGRES_DB: nexus
    ports:
      - "5432:5432"
    volumes:
      - nexus_pg:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  nexus_pg:
```
> The username/password/db here (`nexus`/`nexus`/`nexus`) **must match** what's in your `.env` `DATABASE_URL`. They do. The `volumes` line means your data survives restarts.

### `app/config.py`
Loads the two URLs from `.env` into a typed object.
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str


settings = Settings()
```

### `app/db.py`
Sets up the connections and two tiny "are you alive?" ping functions.
```python
import redis.asyncio as aioredis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

# One database engine for the whole app.
engine = create_async_engine(settings.database_url, pool_pre_ping=True)

# One Redis client for the whole app.
redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)


async def ping_db() -> None:
    """Runs a trivial query. Raises if the DB is unreachable."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def ping_redis() -> None:
    """Pings Redis. Raises if unreachable."""
    await redis_client.ping()
```

### `app/main.py`
The actual web server, with a simple `/` route and the `/health` check.
```python
from fastapi import FastAPI

from app.db import ping_db, ping_redis

app = FastAPI(title="Nexus")


async def _check(check_fn) -> str:
    """Runs a ping function and reports 'ok' or the error name."""
    try:
        await check_fn()
        return "ok"
    except Exception as exc:  # noqa: BLE001 - we want any failure reported
        return f"error: {type(exc).__name__}"


@app.get("/")
async def root():
    return {"app": "Nexus", "message": "It lives."}


@app.get("/health")
async def health():
    db = await _check(ping_db)
    redis = await _check(ping_redis)
    status = "ok" if db == "ok" and redis == "ok" else "degraded"
    return {"status": status, "db": db, "redis": redis}
```

### `tests/test_health.py`
Our first test — checks the `/` route works. (We test `/` not `/health` on purpose: `/` needs no database, so this test passes anywhere, even later in CI.)
```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "Nexus"
```

---

## Step 8 — Bring it to life

### 8a. Start the database + cache
Make sure **Docker Desktop is open**, then:
```bash
docker compose up -d
```
The `-d` means "in the background." First time, it downloads Postgres and Redis — give it a minute.

Check they're running:
```bash
docker ps
```
✅ You should see **two** rows: one `postgres:16`, one `redis:7`.

### 8b. Start your server
```bash
uv run uvicorn app.main:app --reload
```
Breaking that down: `uv run` uses your project's environment; `uvicorn` is the server; `app.main:app` means "the `app` object inside `app/main.py`"; `--reload` restarts automatically when you save a file.

✅ You should see `Uvicorn running on http://127.0.0.1:8000`.

### 8c. See it work
Open your browser to **http://127.0.0.1:8000/health**

✅ You should see:
```json
{"status":"ok","db":"ok","redis":"ok"}
```

**That's the sprint.** Server alive, database alive, cache alive.

Bonus: open **http://127.0.0.1:8000/docs** — FastAPI auto-generates an interactive API page for free. You'll use this constantly.

### 8d. Run the test
Open a **second terminal** (leave the server running in the first), in the same folder:
```bash
uv run pytest
```
✅ `1 passed`.

### 8e. Run the linter
```bash
uv run ruff check .
```
✅ `All checks passed!` (or it'll tell you exactly what to fix.)

---

## Step 9 — Save your work to GitHub

Stop the server for a moment (`Ctrl+C` in its terminal) or use your second terminal:
```bash
git add .
git commit -m "Sprint 0: FastAPI skeleton with Postgres + Redis health check"
git push
```
✅ Refresh your GitHub repo page — your code is there.

> Do this at the end of **every** work session, not just end of sprint. `commit` = save point. `push` = upload the save to the cloud.

---

## ✅ Sprint 0 is done when...

- [ ] `uv --version`, `git --version`, `docker ps` all work
- [ ] GitHub repo `nexus` exists and you've cloned it
- [ ] `docker compose up -d` shows Postgres + Redis running
- [ ] Browser shows `{"status":"ok","db":"ok","redis":"ok"}` at `/health`
- [ ] `uv run pytest` → 1 passed
- [ ] `docs/adr-001-database.md` is written (database decision locked)
- [ ] Everything is committed and pushed to GitHub

If all boxes are ticked — **you built the crafting table. Sprint 0 complete.** 🎉

---

## 🧯 When something breaks (it will — that's normal)

| What you see | What it means | Fix |
|---|---|---|
| `uv: command not found` | New terminal didn't pick up uv | Fully close and reopen the terminal |
| `Cannot connect to the Docker daemon` | Docker Desktop isn't running | Open the Docker Desktop app, wait for it to settle |
| `port 5432 is already allocated` | You already have Postgres running on your machine | Stop your other Postgres, **or** change `"5432:5432"` to `"5433:5432"` in docker-compose.yml **and** update `.env` to `...localhost:5433...` |
| `/health` shows `db: "error: ..."` | Server can't reach Postgres | Is `docker ps` showing postgres? Does `.env` match the docker-compose credentials? |
| `/health` shows `redis: "error: ..."` | Server can't reach Redis | Is `docker ps` showing redis? Is `REDIS_URL` correct in `.env`? |
| `ModuleNotFoundError: No module named 'app'` | Run from the wrong folder | Run commands from inside the `nexus` folder (where `app/` lives) |
| `pydantic ... field required (database_url)` | `.env` not found or empty | Make sure `.env` exists in the `nexus` folder with both URLs |
| Server won't start, red errors | Usually a typo when pasting | Read the last line of the error — it names the file and line |

**General rule when stuck:** read the **last line** of the error message first — Python puts the actual problem there. Paste that line into a search engine or ask me. Don't panic at the wall of text above it; the bottom line is the clue.

---

## What's next (Sprint 1 preview)

Now that the workbench runs, Sprint 1 gives it a memory: real database tables (users, quests, events) and loading your quest list into the database. I'll write it in this same hand-held style when you're ready.

For now: **get the green `ok` on your screen.** That's the only goal this week.
