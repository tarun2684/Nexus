# Project: Level Up — Requirements & Build Document

**Type:** Personal / recreational, multi-user web app (a "sidekick" learning project)
**Owner:** Tarun
**Audience / users:** You + ~10–20 friends (one private group)
**Core idea:** A Minecraft/pixel-themed, RPG-style life & habit tracker. You complete real-life quests (study, open source, DSA, fitness, etc.), earn XP/coins, level up, keep streaks, compete on a weekly leaderboard, share photos, and get help from an AI "sidekick" NPC.
**Stack decision:** FastAPI (Python) backend · PostgreSQL · Redis · AI via LLM API · React PWA frontend.

---

## 1. Goals & Non-Goals

### 1.1 Goals
- Turn daily habits into a game with durable, per-day progress that survives across devices and sessions.
- Support a small private group: accounts, a weekly leaderboard, photo sharing, and an activity feed.
- Integrate an AI sidekick that generates personalized quests, reviews your week, and lets you log activity in plain language.
- Be a vehicle for learning: FastAPI, async Python, Postgres, Redis/queues, auth, and practical LLM integration.

### 1.2 Non-Goals (keep scope sane)
- Not a public product; no marketing, billing, or scale beyond ~50 users.
- No mobile native apps — a installable PWA covers PC + phone.
- No complex social graph — one shared group, not friend requests/DMs.
- No heavy moderation system — a simple delete/report is enough among friends.

### 1.3 Success criteria
- You and your friends actually use it for weeks (streaks stay alive).
- Adding a new quest type or AI feature takes minutes, not a rewrite.
- Runs on free/cheap hosting with near-zero maintenance.

---

## 2. Users & Personas

| Persona | Description | Key needs |
|---|---|---|
| **You (admin)** | Builder + player | Full control, invite friends, tune quests, see everyone's stats |
| **Friend (player)** | Invited user | Log quests fast, see own progress, compete on leaderboard, share wins |
| **AI Sidekick (system actor)** | LLM-driven NPC | Generates quests, reviews weeks, parses natural-language logs |

Access is **invite-only**. No open sign-up.

---

## 3. Functional Requirements

### 3.1 Core game engine (single source of truth: the server)
- **XP & levels:** Cumulative XP; interpolated level curve (L1=0 → L100=500k). Rank tiers (Beginner → Master).
- **Quests:** Categories — Main, Side, Health, Leisure, plus Penalties. Each quest has an id, XP value, coin value, and optional stat it increments.
- **Coins & shop:** Earn coins from high-value quests; spend on rewards (incl. a "Code Shield" that protects a streak, limited once/week).
- **Streaks:** Daily streak that increments on any positive quest, resets on a missed day (unless a shield is active). Milestone rewards at 3/7/14/30/60/100 days.
- **Combos:** Auto-fire once/day when their component quests are all completed (e.g., Morning Warrior, Deep Work Ultra, Perfect Day).
- **Boss battles:** One high-difficulty weekly objective → large XP + coins + trophy.
- **Achievements:** Auto-unlock from stats (PRs merged, DSA solved, runs, papers…) + a few manual "I really did this" claims.
- **Daily/weekly/monthly rollover:** Reset daily quests, roll weekly leaderboard windows, aggregate monthly tournament stats.

### 3.2 Multi-user & social
- **Accounts & auth:** Invite-only login (magic link or Google). Each user has a profile (name, avatar, totals).
- **Weekly leaderboard:** Ranking of all group members by XP earned in the current ISO week. Updates live-ish. Show rank, name, weekly XP, streak.
- **Photo sharing:** Users post a photo + caption (e.g., "gym done", "shipped a feature"), optionally tagged to a quest. Appears in a shared feed.
- **Activity feed:** Chronological list of notable events (level-ups, boss kills, achievements, photo posts) across the group.
- **Reactions (optional):** Emoji reactions on feed items / photos.

### 3.3 AI sidekick features (see §7 for design)
- **Personalized quest generation:** Given a user's goals + recent history, generate a fresh side quest with XP/coins.
- **Natural-language logging:** "I studied ML for 2 hours and went for a run" → parsed into quest completions the server awards.
- **Weekly review / coaching:** A short, in-character (NPC) summary of the user's week with one concrete suggestion.
- **Difficulty & balance hints (stretch):** Flag when a user is over/under-loading a category.

### 3.4 Admin
- Invite/remove users, edit the quest catalog, adjust XP values, and (rarely) correct a user's totals with an audited event.

---

## 4. Non-Functional Requirements

- **Security:** Server-authoritative XP (clients never send XP amounts). Row-level data isolation. Rate limiting on write + AI endpoints. Invite-only.
- **Privacy:** Photos are group-only via signed URLs; users can delete their own posts; no third-party sharing.
- **Performance:** Sub-300ms for normal reads at this scale; leaderboard cached in Redis.
- **Availability:** "Good enough" — free-tier hosting; occasional cold starts acceptable.
- **Cost:** Target $0–$10/month. Cap AI spend with per-user rate limits and a monthly budget guard.
- **Data durability:** Every state change is an append-only event → full history, easy recovery, easy charts.
- **Portability:** Dockerized backend so you can move hosts freely.

---

## 5. System Architecture

```
[ React PWA ]  ──HTTPS/JSON──▶  [ FastAPI ]  ──▶  [ PostgreSQL ]
   (browser)                        │      ├──▶  [ Redis: cache + queue + rate limit ]
   Realtime/WS ◀────────────────────┘      ├──▶  [ Object Storage: photos ]
                                            └──▶  [ LLM API: AI sidekick ]
                        [ ARQ/Celery worker ] ──▶ scheduled rollovers, weekly reset, reminders
```

**Why these pieces**
- **FastAPI** — async, Pydantic-typed, great DX; your Python home turf and pairs with future ML work.
- **PostgreSQL** — relational integrity for events/leaderboards; JSONB for flexible per-day data.
- **Redis** — leaderboard sorted-sets, rate limiting, and the job queue.
- **Object storage** — photos don't belong in Postgres.
- **LLM API** — the AI sidekick.

**Hosting the DB + storage:** Easiest is **Supabase** (managed Postgres + Auth + Storage in one) with FastAPI as your business-logic/AI layer that verifies Supabase JWTs. Alternative: **Neon** (Postgres) + **Cloudflare R2**/S3 (storage) + your own auth (`fastapi-users`). Pick Supabase to move faster; pick Neon+R2 if you want to build auth/storage yourself as a learning exercise.

---

## 6. Data Model (starting schema)

Model as **event ledger + snapshots** — append-only history plus fast-read summaries.

| Table | Key columns | Purpose |
|---|---|---|
| `users` | id, email, display_name, avatar, role, created_at | Accounts |
| `profiles` | user_id, total_xp, coins, trophies, streak_count, streak_longest, last_active, level | Fast read of "current state" |
| `events` | id, user_id, ts, type, xp_delta, coin_delta, quest_id, meta jsonb | **Append-only log** — the source of truth |
| `daily_logs` | user_id, date, xp_earned, quests_done jsonb, combos jsonb | One row per user per day (your "every day's progress") |
| `quests` | id, category, title, xp, coins, stat_key, active | Editable quest catalog (seeded) |
| `achievements` | user_id, ach_id, unlocked_at | Unlocked achievements |
| `posts` | id, user_id, photo_path, caption, quest_id, created_at | Photo feed |
| `reactions` | id, post_id, user_id, emoji | Optional |
| `invites` | id, code/email, created_by, used_by, expires_at | Invite-only access |
| `ai_calls` | id, user_id, ts, feature, tokens, cost | AI usage/budget tracking |

**Leaderboard is a query, not a table:** sum `events.xp_delta` where `ts` is in the current ISO week, grouped by user. Cache the result in a Redis sorted set for live updates; no "reset job" needed because you filter by week window.

---

## 7. AI Integration Design (the fun part)

### 7.1 Where AI adds value
1. **Quest generator** — input: user goals + last N days of activity; output: one quest `{title, category, xp, coins, rationale}` as **structured JSON**.
2. **Natural-language logger** — input: free text; output: a list of matched `quest_id`s (mapped against your catalog) that the **server** then validates and awards. Never let the model set XP directly — it only classifies; the server assigns points.
3. **Weekly reviewer / NPC coach** — input: weekly stats; output: a short in-character message + one actionable tip.
4. **(Stretch) Balance advisor** — detect neglected categories and nudge.

### 7.2 How to build it safely
- Use the provider's official **Python SDK**; request **structured/JSON output** and validate with **Pydantic** before use.
- **The AI never mutates game state.** It returns suggestions/classifications; your FastAPI code applies rules and writes events. This preserves anti-cheat.
- **Guardrails:** cap tokens, set per-user rate limits (Redis), log every call in `ai_calls`, and enforce a monthly budget ceiling that disables AI features if exceeded.
- **Prompt hygiene:** treat user text as data, not instructions; keep a fixed system prompt describing the NPC persona and the exact JSON schema you expect.
- **Caching:** cache weekly reviews and generated-quest pools to cut cost.

### 7.3 Provider options
- **Hosted API** (Anthropic Claude or OpenAI) — simplest, best quality, pay per use. Start here.
- **Local models via Ollama** — free, private, and a great ML-learning exercise; slower/weaker. Good as a later swap behind the same interface.
- Wrap whichever you pick behind one `ai_service` module so you can switch providers without touching the rest of the app.

---

## 8. API Surface (representative)

| Method & path | Purpose | Notes |
|---|---|---|
| `POST /auth/verify` | Exchange/verify login token | Invite-only |
| `GET /me/state` | Current profile + today's quests | Read snapshot |
| `POST /quests/{id}/complete` | Complete a quest | **Server assigns XP**, writes event, checks combos/achievements |
| `POST /penalties/{id}` | Apply a penalty | |
| `POST /shop/{item}/buy` | Spend coins | Enforces shield once/week |
| `GET /leaderboard/week` | Weekly ranking | Redis-cached |
| `GET /feed` | Activity + photo feed | Paginated |
| `POST /posts` | Upload photo + caption | Signed upload → store metadata |
| `POST /ai/quest` | Generate a personalized quest | Rate-limited, budgeted |
| `POST /ai/log` | Parse NL activity → quests | Server validates & awards |
| `GET /ai/weekly-review` | NPC weekly summary | Cached |
| `GET /me/history` | XP/streak over time | Powers charts |

All write endpoints: authenticated, rate-limited, and validated with Pydantic.

---

## 9. Anti-Cheat & Security Checklist
- [ ] XP/coins computed **only** on the server from the quest catalog.
- [ ] Auth on every endpoint; users can only read/write their own rows (RLS or explicit `user_id` scoping).
- [ ] Rate limit quest completes (e.g., each quest once/day) and AI calls.
- [ ] Photos: size/type limits, client-side compression, signed URLs, owner-only delete.
- [ ] Secrets (DB URL, API keys) in env vars, never in the frontend.
- [ ] Admin corrections go through an **audited event**, not a raw DB edit.

---

## 10. Tech Stack & Tools

| Layer | Choice | Alt / notes |
|---|---|---|
| Backend | **FastAPI** | Uvicorn/Gunicorn to serve |
| ORM & schemas | **SQLModel** (or SQLAlchemy 2.0 async + Pydantic) | `asyncpg` driver |
| Migrations | **Alembic** | |
| DB | **PostgreSQL** (Supabase or Neon) | |
| Cache/queue | **Redis** (Upstash) | |
| Background jobs | **ARQ** (async, Redis) or **Celery** | Your Python analog to BullMQ |
| Auth | **Supabase Auth** (verify JWT in FastAPI) or `fastapi-users` | Invite-only |
| Storage | **Supabase Storage** or **Cloudflare R2/S3** | Photos |
| Realtime | **Supabase Realtime** or FastAPI **WebSockets** | Live leaderboard/feed |
| AI | LLM API via official Python SDK (+ Pydantic validation) | Ollama later |
| Frontend | **React (Vite) PWA** or Next.js | Keep the pixel theme |
| Tests | **pytest** + httpx | Cover the XP/streak/combo logic |
| Container | **Docker** | Portability |

---

## 11. Hosting & Deployment

- **Frontend (PWA):** Vercel / Netlify / Cloudflare Pages — free.
- **FastAPI backend:** Railway, Render, or Fly.io (Docker). A few $/month or free tier.
- **Postgres + Storage + Auth:** Supabase free tier (~500 MB DB, 1 GB storage) — plenty for 20 friends; **compress photos** to stay within it.
- **Redis:** Upstash serverless free tier.
- **AI:** pay-as-you-go; guard with the budget ceiling above.
- **HTTPS:** required for the PWA/service worker (hosts provide it).
- **CI/CD:** GitHub Actions → build Docker image + run tests + deploy on push.
- **Estimated cost:** ~$0–$10/month until you outgrow free tiers.

---

## 12. Build Roadmap (phased)

1. **Foundation:** FastAPI skeleton, Postgres, SQLModel, Alembic, Docker, one `/health` route.
2. **Game engine + persistence:** quests, events, daily_logs, XP/level/streak/combo logic, pytest coverage. Single-user.
3. **Auth + multi-user:** invite-only login, per-user scoping, profiles.
4. **Leaderboard:** weekly SQL query → Redis sorted set → live updates.
5. **Photos + feed:** storage uploads, `posts`, feed endpoint, reactions.
6. **AI sidekick:** `ai_service` module, quest generator + NL logger (structured output + Pydantic), budget guard.
7. **Scheduled jobs:** ARQ worker for rollovers, weekly reset windows, reminders.
8. **PWA + deploy:** manifest, service worker, host everything, invite friends.
9. **Polish/extend:** charts, streak heatmap, weekly review, notifications, GitHub API auto-credit for PRs/issues.

---

## 13. What You'll Learn (mapped to phases)
- **FastAPI + async Python + Pydantic** (phases 1–2)
- **Relational modeling, event sourcing, migrations** (phase 2)
- **Auth, JWTs, authorization/data isolation** (phase 3)
- **Redis: caching, sorted sets, rate limiting** (phases 4, 6)
- **Object storage & file handling** (phase 5)
- **Practical LLM integration: structured outputs, prompt safety, cost control** (phase 6) — directly relevant to your ML-security direction
- **Background jobs / schedulers** (phase 7)
- **PWA, CI/CD, Docker, cloud deploy** (phase 8)

---

## 14. Risks & Things to Watch
- **AI cost creep** → per-user limits + monthly ceiling + caching.
- **Cheating on the leaderboard** → server-authoritative XP, once/day limits, audited admin edits.
- **Storage bloat from photos** → compress + resize + size caps.
- **Free-tier cold starts / DB pausing** → acceptable here; upgrade one service if it annoys you.
- **Scope creep** → this is recreational; ship phases, don't gold-plate.
- **Prompt injection via user text** → treat all user input as data; fixed system prompt + schema validation.

---

## 15. Open Decisions (make these before phase 3)
- Supabase (fast) **vs** Neon + R2 + your own auth (more to learn)?
- One shared group **vs** multiple groups later?
- AI provider: hosted API first, Ollama later — confirm.
- Reactions/feed in v1 or v2?
- Reminders channel: web-push, email, or none for v1?

---

*Living document — refine as you build. Suggested next artifact: the SQLModel schema + Alembic setup and the server-authoritative `complete_quest` endpoint (phases 1–2), since everything else hangs off that backbone.*
