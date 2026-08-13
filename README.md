<div align="center">

# ⚔️ Nexus

**An RPG-style life & habit tracker for you and your friends.**

Turn real-life habits — studying, shipping code, training, reading — into quests, XP, streaks, and a weekly leaderboard.

[![Status](https://img.shields.io/badge/status-pre--code%20%2F%20planning-yellow)](#project-status)
[![Stack](https://img.shields.io/badge/backend-FastAPI-009688)](#tech-stack)
[![Stack](https://img.shields.io/badge/db-PostgreSQL-336791)](#tech-stack)
[![License](https://img.shields.io/badge/license-TBD-lightgrey)](#license)

</div>

---

## Overview

**Nexus** (working title *Level Up*) is a Minecraft/pixel-themed, RPG-style life & habit tracker built as a private multi-user web app for a small friend group. You complete real-life quests, earn XP and coins, level up, keep daily streaks, compete on a weekly leaderboard, share progress photos, and get coaching from an AI "sidekick" NPC.

It's also a deliberate learning project — a vehicle for going deep on FastAPI, async Python, PostgreSQL, Redis, auth, and practical LLM integration.

## Features

- **Quest system** — Main, Side, Health, and Leisure quests, plus penalties, each with XP and coin rewards
- **XP & levels** — cumulative XP against an interpolated level curve, with rank tiers from Beginner to Master
- **Streaks & combos** — daily streaks with milestone rewards, and auto-firing combos (e.g. *Morning Warrior*, *Deep Work Ultra*) when quest sets are completed together
- **Boss battles** — a high-difficulty weekly objective for a large XP/coin/trophy payout
- **Achievements** — auto-unlocked from stats, plus a few manual claims
- **Weekly leaderboard** — live-ish ranking of the group by weekly XP
- **Social feed** — photo sharing and a chronological activity feed (level-ups, boss kills, achievements)
- **AI sidekick** — generates personalized quests, parses natural-language activity logs ("studied ML for 2 hours and went for a run"), and delivers a weekly, in-character review

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | FastAPI (Python, async) |
| Database | PostgreSQL (via SQLModel + Alembic) |
| Cache / Queue | Redis (leaderboard, rate limiting, job queue) |
| Background jobs | ARQ / Celery worker (rollovers, weekly resets, reminders) |
| Object storage | Cloudflare R2 (photos, signed URLs) |
| AI | LLM API (quest generation, NL logging, weekly reviews) |
| Frontend | React (installable PWA) |

```
[ React PWA ]  ──HTTPS/JSON──▶  [ FastAPI ]  ──▶  [ PostgreSQL ]
   (browser)                        │      ├──▶  [ Redis: cache + queue + rate limit ]
   Realtime/WS ◀────────────────────┘      ├──▶  [ Object Storage: photos ]
                                            └──▶  [ LLM API: AI sidekick ]
                        [ ARQ/Celery worker ] ──▶ scheduled rollovers, weekly reset, reminders
```

**Design principles:** server-authoritative XP (clients never send XP amounts), append-only event log as the source of truth for every state change, invite-only access, and a cost target of $0–$10/month on free-tier hosting.

## Project Status

🚧 **Sprint 0 (Groundwork) — code complete, pending local infra.** The FastAPI skeleton, config, `/health` check, tests, and ADR are written and passing (`pytest`, `ruff check .`). Still needed on the dev machine: Docker Desktop (for Postgres + Redis) and `uv`, then `docker compose up -d` to get a fully live `{"status":"ok","db":"ok","redis":"ok"}`. Track progress via the docs below.

## Documentation

| Doc | Description |
|---|---|
| [level-up-requirements.md](level-up-requirements.md) | Full requirements: goals, personas, functional & non-functional requirements, architecture |
| [nexus-action-plan.md](nexus-action-plan.md) | Master action plan / checklist across all sprints |
| [nexus-sprint-0-tasks.md](nexus-sprint-0-tasks.md) | Sprint 0 — groundwork: repo, tooling, local infra, ADR |
| [nexus-sprint-1-tasks.md](nexus-sprint-1-tasks.md) | Sprint 1 — data foundation: models, migrations, seed data |
| [nexus-sprint-2-tasks.md](nexus-sprint-2-tasks.md) | Sprint 2 ⭐ (M1) — the game engine: level curve, streaks, combos, achievements |

## Getting Started

Nexus isn't runnable yet. [nexus-sprint-0-tasks.md](nexus-sprint-0-tasks.md) covers the groundwork to stand up a working skeleton: repo scaffolding, a Docker Compose stack (Postgres + Redis), and a first `/health` endpoint. This section will be filled in with real setup instructions once that milestone lands.

## License

TBD.
