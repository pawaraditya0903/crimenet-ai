# CrimeNet AI — Security Audit Report
**Audit Date:** 2026-09-17  
**Auditor:** Antigravity Full-Stack Security Review  
**Scope:** Full repository — backend, frontend, DevOps, database, ML, graph  
**Environment:** Academic prototype with production-grade security requirements

---

## Executive Summary

CrimeNet AI has a solid architectural foundation (separate PostgreSQL, Neo4j, and MinIO services; RBAC with case-level IDOR prevention; hash-linked audit chain; Merkle evidence tree). However, a number of **real and directly exploitable** security defects were found that would be unacceptable in any operational deployment.

**The most critical findings are:**
1. Evidence bucket publicly readable by anyone — no authentication required
2. Real credentials committed to version-controlled `.env` and `.env.example`
3. Hardcoded password `Aditya@4912` in both backend source and frontend TypeScript
4. Passwordless auto-login via URL path pattern bypasses all authentication
5. Path traversal vulnerability in local evidence vault fallback

---

## Finding Index

| ID | Severity | Title | Status |
|----|----------|-------|--------|
| SEC-001 | 🔴 **Critical** | Public/anonymous read access on MinIO evidence bucket | ✅ Fixed |
| SEC-002 | 🔴 **Critical** | Real credentials committed to `.env.example` (tracked by git) | ✅ Fixed |
| SEC-003 | 🔴 **Critical** | Password `Aditya@4912` hardcoded in `main.py`, `tables.py`, `App.tsx` | ✅ Fixed |
| SEC-004 | 🔴 **Critical** | Passwordless jury/demo bypass auto-authenticates as Chief Officer | ✅ Fixed |
| SEC-005 | 🔴 **Critical** | Path traversal in local evidence vault — user filename used as storage path | ✅ Fixed |
| SEC-006 | 🟠 **High** | 8+ graph/analytics/entity endpoints require no authentication | ✅ Fixed |
| SEC-007 | 🟠 **High** | Evidence download serves DB-stored MIME type without validation — XSS vector | ✅ Fixed |
| SEC-008 | 🟠 **High** | `/api/notifications` authentication optional — data leaks to unauthenticated callers | ✅ Fixed |
| SEC-009 | 🟠 **High** | Simulation endpoints unauthenticated — global state mutatable by anyone | ✅ Fixed |
| SEC-010 | 🟠 **High** | Rate limiting in-memory only — bypassed by multiple workers, resets on restart | ⚠️ Documented |
| SEC-011 | 🟠 **High** | Default MinIO/PostgreSQL credentials not blocked in production | ✅ Fixed |
| SEC-012 | 🟠 **High** | Biometric login accepts client-supplied `similarity_score` — score injection | ✅ Fixed |
| SEC-013 | 🟠 **High** | Evidence download/upload lacks case-level access check — cross-case IDOR | ✅ Fixed |
| SEC-014 | 🟠 **High** | JWT stored in both `localStorage` and `sessionStorage` — XSS token theft risk | ✅ Fixed |
| SEC-015 | 🟡 **Medium** | ML anomaly outputs lack mandatory responsible-AI disclaimers | ✅ Fixed |
| SEC-016 | 🟡 **Medium** | Audit chain stored in mutable SQLite — administrator can rewrite entries | ⚠️ Documented |
| SEC-017 | 🟡 **Medium** | Production mode silently falls back to SQLite when PostgreSQL fails | ✅ Fixed |
| SEC-018 | 🟡 **Medium** | Neo4j NetworkX fallback mode not surfaced — UI shows stale data silently | ✅ Fixed |
| SEC-019 | 🟡 **Medium** | `X-Forwarded-For` trusted for rate-limiting without IP validation | ⚠️ Documented |
| SEC-020 | 🟡 **Medium** | MinIO console port 9001 publicly bound (not localhost-only) | ✅ Fixed |
| SEC-021 | 🟡 **Medium** | No MIME type allowlist on evidence upload | ✅ Fixed |
| SEC-022 | 🟡 **Medium** | Merkle root endpoint unauthenticated — evidence index publicly readable | ✅ Fixed |
| SEC-023 | 🟡 **Medium** | `create_all()` and Alembic both manage schema — risk of divergence | ⚠️ Documented |
| SEC-024 | 🟡 **Medium** | Evidence object keys incorporate user-supplied filename — partial path traversal | ✅ Fixed |
| SEC-025 | 🟢 **Low** | `ENVIRONMENT=enterprise` not treated as production — weak credential checks skipped | ✅ Fixed |
| SEC-026 | 🟢 **Low** | `ErrorBoundary` renders raw JavaScript error messages to end users | ✅ Fixed |
| SEC-027 | 🟢 **Low** | Pipeline summary endpoint publicly exposes internal graph topology counts | ✅ Fixed |
| SEC-028 | 🟢 **Low** | Neo4j URI included in health check response — credentials exposure risk | ✅ Fixed |

---

## Detailed Findings

### SEC-001 — Critical: Public Anonymous Evidence Bucket
**File:** `docker-compose.yml`  
**Original code:** `mc anonymous set download local/${S3_BUCKET_NAME}`  
**Risk:** Any actor who can reach the MinIO endpoint can enumerate and download all evidence objects without any credentials — including CDR exports, ANPR footage, and banking records.  
**Fix:** Removed the `mc anonymous set download` command entirely. The bucket is created as private. All evidence access routes through the authenticated `/api/evidence/download/{id}` backend endpoint.

### SEC-002 — Critical: Real Secrets in Version-Controlled Files
**Files:** `.env`, `.env.example`  
**Risk:** The actual 64-character JWT signing secret, PII encryption key, and MinIO credentials were committed to `.env.example` (tracked by git). Anyone with repository access could use these to forge JWT tokens, decrypt PII fields, and access object storage.  
**Fix:** `.env.example` now uses clearly-marked placeholder strings (`REPLACE_WITH_...`). The live `.env` has been sanitized. Both committed secrets must be rotated immediately (see remediation steps below).

> **IMMEDIATE ACTION REQUIRED:** Rotate `CRIMENET_JWT_SECRET`, `CRIMENET_PII_ENCRYPTION_KEY`, `S3_ACCESS_KEY`, and `S3_SECRET_KEY` before any further deployment.

### SEC-003 — Critical: Hardcoded Password in Source Code
**Files:** `backend/app/main.py`, `backend/app/models/tables.py`, `frontend/src/App.tsx`  
**Original code:** `hash_password("Aditya@4912")`, `password: 'Aditya@4912'`  
**Risk:** The actual administrative password is committed as a plaintext literal, making it trivially extractable from any git clone or code review.  
**Fix:** Seed password now sourced from `DEFAULT_SEED_PASSWORD` env variable. Frontend auto-login code completely removed. Password literal eliminated from all source files.

### SEC-004 — Critical: Passwordless Jury/Demo URL Bypass
**File:** `frontend/src/App.tsx`  
**Original code:** URL paths containing `/jury`, `/demo`, `demo=sih2026`, `access=jury` triggered automatic login as Chief Officer (`SUPERVISORY_OFFICER` role) using the hardcoded password.  
**Risk:** Any person who visits `https://app.example.com/demo` gets full supervisor-level access without entering credentials. The `catch()` handler even grants access if the API call fails — making authentication truly optional.  
**Fix:** Entire jury bypass block removed. All visitors must use the standard login screen.

### SEC-005 — Critical: Path Traversal in Local Evidence Vault
**File:** `backend/app/storage/s3_client.py`  
**Original code:** `os.path.join(LOCAL_VAULT_DIR, clean_key)` used without resolving the canonical path first.  
**Attack:** `filename = "../../etc/passwd"` → `object_key = "evidence/c1/ev-abc_../../etc/passwd"` → `os.path.join("/vault", "evidence/c1/ev-abc_../../etc/passwd")` = `/vault/etc/passwd` traversal.  
**Fix:** `pathlib.Path.resolve()` used for all vault paths. Final path validated to be `relative_to(LOCAL_VAULT_DIR)` before any read or write. Object keys also validated against a safe-character regex.

### SEC-006 — High: Unauthenticated Graph & Analytics Endpoints
**File:** `backend/app/routers/graph.py`  
**Endpoints:** `/api/graph/network`, `/api/entities/all`, `/api/entities/search`, `/api/relationships/all`, `/api/analytics/top-influencers`, `/api/analytics/communities`, `/api/analytics/network-stats`, `/api/analytics/run`, `/api/analytics/shortest-path`  
**Risk:** Full criminal intelligence network data — suspect names, entity risk scores, relationship types — is accessible to unauthenticated callers.  
**Fix:** `require_authenticated_user` dependency added to all endpoints. Added pagination limits to prevent unbounded responses.

### SEC-007 — High: Unvalidated MIME Type in Evidence Download
**File:** `backend/app/routers/evidence.py`  
**Risk:** If an evidence item was uploaded with `Content-Type: text/html`, the download endpoint would serve it with `media_type="text/html"`. If opened in a browser, this could trigger XSS execution.  
**Fix:** MIME type validated against `_SAFE_SERVE_TYPES` allowlist before serving. Unknown types default to `application/octet-stream`. `Content-Disposition: attachment` forced on all downloads. `X-Content-Type-Options: nosniff` header added.

### SEC-008 — High: Unauthenticated Notifications Endpoint
**File:** `backend/app/main.py`  
**Original:** `claims: Optional[dict] = None` — authentication was optional, returning all notifications to unauthenticated callers.  
**Fix:** Changed to `claims: dict = Depends(require_authenticated_user)`. Non-supervisors now only receive their own notifications.

### SEC-009 — High: Unauthenticated Simulation State Endpoints
**File:** `backend/app/main.py`  
**Endpoints:** `/api/sim/start`, `/api/sim/pause`, `/api/sim/reset`, `/api/simulation/speed`  
**Risk:** Any unauthenticated caller can start, stop, or reset the live telemetry simulation — disrupting ongoing investigations or generating misleading alerts.  
**Fix:** `require_authenticated_user` dependency added to all simulation endpoints.

### SEC-010 — High: In-Memory Rate Limiting (Documented)
**File:** `backend/app/security/rate_limit.py`  
**Risk:** The sliding-window rate limiter and account lockout state are stored in process memory (`defaultdict`). With multiple Uvicorn workers, each worker has independent state, so an attacker can bypass limits by distributing requests across workers. State also resets on restart, re-enabling brute force.  
**Recommendation:** Use Redis (`redis-py` or `fastapi-limiter`) as shared rate-limit storage. The fix requires infrastructure changes beyond the scope of this patch but is tracked.

### SEC-011 — High: Default Credentials Not Blocked in Production
**File:** `backend/app/config.py`  
**Risk:** `postgres/postgres` and `minioadmin/minioadmin` were permitted in all environments.  
**Fix:** Added `WEAK_DB_PASSWORDS`, `WEAK_MINIO_CREDENTIALS`, and `WEAK_NEO4J_PASSWORDS` sets. In `production` or `enterprise` mode, startup fails with a clear error message if any detected credential is in the weak set.

### SEC-012 — High: Biometric Score Injection
**File:** `backend/app/routers/auth.py`  
**Original:** `elif req.similarity_score is not None: similarity = req.similarity_score` — the client could send `{ "similarity_score": 100.0 }` and receive a token with no actual biometric probe.  
**Fix:** The `similarity_score` code path completely removed. Server-side vector evaluation via `evaluate_face_prototype()` is now the only permitted path.

### SEC-013 — High: Cross-Case Evidence IDOR
**File:** `backend/app/routers/evidence.py`  
**Risk:** Authenticated user `usr-03` (Forensic Analyst Verma, assigned only to case `c1`) could call `GET /api/evidence/download/ev-03` (belonging to case `c2`) and download it successfully.  
**Fix:** `_verify_case_access(case_id, user_id, role)` called before all upload and download operations. Returns 403 if the user is not assigned to the case and is not a `SUPERVISORY_OFFICER`.

### SEC-014 — High: JWT Stored in localStorage
**File:** `frontend/src/lib/api.ts`, `frontend/src/App.tsx`  
**Risk:** `localStorage` is accessible to any JavaScript running on the page. If any dependency or injected script achieves XSS, the JWT token can be exfiltrated and used to impersonate the user indefinitely (tokens last 15 minutes by default).  
**Fix:** Token storage migrated to `sessionStorage` exclusively. `localStorage.setItem('crimenet_jwt_token', ...)` calls removed. `clearStoredToken()` utility cleans both stores. `401` interceptor fires a `crimenet:session-expired` event and purges tokens.

### SEC-015 — Medium: Missing Responsible-AI Disclaimers
**Files:** `backend/app/routers/analytics.py`, `backend/app/routers/graph.py`  
**Risk:** Endpoints returning ML anomaly scores, centrality rankings, or community labels without disclaimers risk being misread as determinations of guilt rather than investigative leads.  
**Fix:** `ML_DISCLAIMER` and `GRAPH_ANALYTICS_DISCLAIMER` strings added and included in all analytics/graph API responses.

### SEC-017 — Medium: Silent SQLite Fallback in Production
**File:** `backend/app/database/connection.py`  
**Risk:** If PostgreSQL was unreachable, the backend silently fell back to SQLite — losing all data from a prior production run, accepting writes to a temporary in-memory/file DB, and returning stale data.  
**Fix:** When `IS_PRODUCTION=True`, any failure to connect to PostgreSQL raises `RuntimeError` and aborts startup.

### SEC-018 — Medium: Neo4j Degraded Mode Not Surfaced
**File:** `backend/app/graph/neo4j_client.py`  
**Risk:** When Neo4j was unavailable, the system used a NetworkX projection silently. The UI could not distinguish live Neo4j data from the static projection.  
**Fix:** `degraded_mode: true` and an explicit warning message added to the status response when NetworkX fallback is active.

### SEC-020 — Medium: MinIO Console Publicly Bound
**File:** `docker-compose.yml`  
**Original:** `- "9001:9001"` (binds to all interfaces)  
**Fix:** `- "127.0.0.1:9001:9001"` — MinIO admin console now accessible on localhost only.

### SEC-021 — Medium: No MIME Allowlist on Upload
**File:** `backend/app/storage/s3_client.py`  
**Risk:** Evidence upload accepted any MIME type including `text/html`, `application/x-sh`, or `application/javascript`.  
**Fix:** `validate_mime_type()` enforces an `ALLOWED_MIME_TYPES` allowlist and a `BLOCKED_MIME_TYPES` denylist. Blocked types raise `ValueError(415)`.

### SEC-024 — Medium: User Filename in Object Key
**Files:** `backend/app/services/evidence_service.py`, `backend/app/storage/s3_client.py`  
**Original:** `object_key = f"evidence/{case_id}/{evidence_id}_{filename}"` (filename is user-controlled)  
**Risk:** Partial path traversal via filename characters that survive the `os.path.join()` call; also leaks filename metadata in storage paths.  
**Fix:** `generate_object_key(case_id, evidence_id)` produces UUID-based paths. User filename stored only as display metadata in the database.

---

## Documented-Only Findings (Infrastructure Constraints)

### SEC-010 — In-Memory Rate Limiting
Current: `defaultdict` in process memory. Limitation: cannot share state across workers.  
Recommendation: `redis-py` + `fastapi-limiter`. Track with: [SEC-010]

### SEC-016 — Audit Chain in Mutable SQLite
Current: `audit_chain` table in SQLite with hash-links.  
Limitation: A database administrator can truncate or rewrite entries. The hash chain detects tampering only after the fact.  
Recommendation: Periodic Merkle root anchoring to an external append-only log (e.g., cloud logging, timestamp authority). Track with: [SEC-016]

### SEC-019 — X-Forwarded-For IP Spoofing for Rate Limits
Current: `X-Forwarded-For` header partially trusted in `extract_real_ip()`.  
Limitation: An attacker can cycle IPs by spoofing this header.  
Recommendation: Only trust `X-Forwarded-For` from known reverse-proxy CIDR ranges. Track with: [SEC-019]

### SEC-023 — Dual Schema Management
Current: Both `Base.metadata.create_all()` and Alembic `env.py` manage the schema.  
Limitation: Risk of divergence between what Alembic thinks the schema is and what `create_all` created.  
Recommendation: Remove `create_all()` from startup; rely solely on Alembic migrations. Track with: [SEC-023]

---

## Immediate Remediation Checklist

- [ ] **Rotate** `CRIMENET_JWT_SECRET` immediately (old secret is public)
- [ ] **Rotate** `CRIMENET_PII_ENCRYPTION_KEY` immediately (old key is public)
- [ ] **Rotate** MinIO `S3_ACCESS_KEY` and `S3_SECRET_KEY`
- [ ] **Revoke** all existing JWT tokens (change secret)
- [ ] **Set** `DEFAULT_SEED_PASSWORD` in `.env` and re-seed
- [ ] **Set** `CRIMENET_ENV=production` in production deployments
- [ ] **Deploy** updated `docker-compose.yml` to remove public bucket access

---

*Report generated: 2026-09-17 UTC*  
*Auditor: Antigravity Security Review*
