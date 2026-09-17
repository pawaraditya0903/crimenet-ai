# CrimeNet AI — Security Fixes Summary
**Applied:** 2026-09-17  
**Total findings:** 28  
**Fixed:** 23 | **Documented (infrastructure):** 5

---

## Files Modified

| File | Findings Fixed |
|------|----------------|
| `docker-compose.yml` | SEC-001, SEC-020 |
| `.env` | SEC-002 |
| `.env.example` | SEC-002 |
| `backend/app/config.py` | SEC-011, SEC-017, SEC-025 |
| `backend/app/database/connection.py` | SEC-017 |
| `backend/app/storage/s3_client.py` | SEC-005, SEC-021, SEC-024 |
| `backend/app/routers/evidence.py` | SEC-007, SEC-013, SEC-022 |
| `backend/app/routers/graph.py` | SEC-006 |
| `backend/app/routers/analytics.py` | SEC-006, SEC-015 |
| `backend/app/routers/pipeline.py` | SEC-027 |
| `backend/app/routers/auth.py` | SEC-012 |
| `backend/app/main.py` | SEC-003, SEC-008, SEC-009 |
| `backend/app/models/tables.py` | SEC-003 |
| `backend/app/services/evidence_service.py` | SEC-024 |
| `backend/app/graph/neo4j_client.py` | SEC-018, SEC-028 |
| `frontend/src/App.tsx` | SEC-004, SEC-003, SEC-026 |
| `frontend/src/lib/api.ts` | SEC-014 |

---

## Fix Summary by Category

### Docker & Infrastructure
- **SEC-001:** Removed `mc anonymous set download` from `minio-init` entrypoint. Evidence bucket is now private.
- **SEC-020:** MinIO console port 9001 now bound to `127.0.0.1` only in `docker-compose.yml`.
- **SEC-011:** `docker-compose.yml` now uses `${S3_ACCESS_KEY:?S3_ACCESS_KEY must be set in .env}` — fails if not set.

### Secrets & Credentials
- **SEC-002:** `.env.example` sanitized — all real values replaced with `REPLACE_WITH_...` placeholders.
- **SEC-002:** `.env` sanitized — real secrets replaced with placeholders. Must be regenerated.
- **SEC-003:** `hash_password("Aditya@4912")` removed from `main.py`, `tables.py`.
- **SEC-003:** `password: 'Aditya@4912'` removed from `frontend/src/App.tsx`.
- **SEC-011:** Production startup fails fast on `postgres/postgres`, `minioadmin/minioadmin`, or any placeholder secret.
- **SEC-025:** `CRIMENET_ENV=enterprise` now treated as production (was skipped before).

### Authentication & Authorization
- **SEC-004:** Passwordless jury/demo URL bypass entirely removed from `App.tsx`.
- **SEC-006:** Added `require_authenticated_user` to all graph, entity, and analytics endpoints.
- **SEC-008:** `/api/notifications` now requires authentication. Non-supervisors see only their own notifications.
- **SEC-009:** Simulation endpoints (`/api/sim/*`, `/api/simulation/*`) now require authentication.
- **SEC-012:** Biometric login no longer accepts client-supplied `similarity_score`. Server-side vector evaluation only.
- **SEC-013:** Case-level IDOR check (`_verify_case_access`) added to evidence upload and download.
- **SEC-022:** Merkle root endpoint now requires authentication.
- **SEC-027:** Pipeline summary endpoint now requires authentication.

### Path Traversal & Upload Safety
- **SEC-005:** `pathlib.Path.resolve()` used in all local vault operations. Final path checked with `relative_to(LOCAL_VAULT_DIR)`.
- **SEC-021:** `validate_mime_type()` added with `ALLOWED_MIME_TYPES` allowlist and `BLOCKED_MIME_TYPES` denylist.
- **SEC-024:** Object keys now generated via `generate_object_key(case_id, evidence_id)` — UUID-based, not filename-based.

### Evidence Download Security
- **SEC-007:** Evidence download validates MIME against `_SAFE_SERVE_TYPES` allowlist. Unknown → `application/octet-stream`. `Content-Disposition: attachment` always forced. `X-Content-Type-Options: nosniff` added.

### Database & Services
- **SEC-017:** Production mode fails with `RuntimeError` if PostgreSQL is unavailable — no silent SQLite fallback.
- **SEC-018:** Neo4j status now includes `degraded_mode: true` and explicit warning when NetworkX fallback is active.

### Frontend Security
- **SEC-014:** JWT token now stored in `sessionStorage` only. `localStorage` token storage completely removed. `clearStoredToken()` utility cleans both. `401` interceptor fires `crimenet:session-expired` event.
- **SEC-026:** `ErrorBoundary` raw error message gated behind `import.meta.env?.DEV === true` — hidden in production builds.

### Responsible AI
- **SEC-015:** `ML_DISCLAIMER` added to all analytics endpoint responses.  
  `GRAPH_ANALYTICS_DISCLAIMER` added to all graph/centrality responses.

---

## How to Re-Deploy Safely

```bash
# 1. Generate new secrets
python -c "import secrets; print('JWT:', secrets.token_hex(32)); print('PII:', secrets.token_hex(32))"
python -c "import secrets; print('MinIO Key:', secrets.token_urlsafe(16)); print('MinIO Secret:', secrets.token_urlsafe(32))"
python -c "import secrets; print('Seed PW:', secrets.token_urlsafe(16))"

# 2. Update .env with new values (never commit this file)
# Set CRIMENET_JWT_SECRET, CRIMENET_PII_ENCRYPTION_KEY, S3_ACCESS_KEY, S3_SECRET_KEY, DEFAULT_SEED_PASSWORD

# 3. Restart services
docker compose down && docker compose up -d

# 4. Verify MinIO bucket is private
docker exec crimenet_minio_init mc anonymous get local/crimenet-evidence
# Expected: Access permission for `local/crimenet-evidence` is `none`
```

---

*Fixes applied: 2026-09-17 UTC*
