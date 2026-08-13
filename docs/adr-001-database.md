# ADR-001: Database, Auth & Storage

**Date:** 2026-08-13
**Decision:** Neon (managed Postgres) + Cloudflare R2 (object storage) + `fastapi-users` (self-rolled auth).

**Why:** This is a deliberate learning project — building auth and object storage
ourselves is part of the point, not overhead to avoid. Neon gives managed
Postgres (no DB ops) without bundling auth/storage decisions we'd rather make
ourselves. R2 is S3-compatible, has a generous free tier, and no egress fees.
`fastapi-users` gives JWT auth we control and can audit, instead of trusting a
third party's auth black box.

**Consequence:** Sprint 5 (auth) wires `fastapi-users` with a JWT strategy.
Sprint 7 (photos) uploads directly to R2 via presigned S3-compatible URLs.
Locally (Sprint 0 onward) Postgres and Redis run via Docker Compose; Neon is
provisioned when we deploy in Sprint 3.

**Revisit if:** self-rolled auth becomes a maintenance burden, or R2/Neon free
tiers stop being enough.
