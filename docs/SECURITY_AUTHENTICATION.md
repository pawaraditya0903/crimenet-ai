# CrimeNet AI: Security & Authentication Architecture

This document specifies the defensive security, cryptography, session lifecycle, and access control model implemented in **CrimeNet AI**.

---

## 1. Threat Profile & Security Invariants

CrimeNet AI handles law enforcement and analytical intelligence data. In order to be technically defensible, the system strictly enforces the following security invariants:

1. **Fail-Closed Production**: If `CRIMENET_ENV=production` is set, the application will abort startup immediately if cryptographic keys or secrets use demo defaults or fail entropy checks.
2. **Zero Plaintext Credentials**: Passwords and refresh tokens are never stored in plaintext.
3. **No Unilateral Execution**: AI systems cannot mutate databases, alter case stages, or execute actions without human officer confirmation.
4. **Horizontal & Vertical Privilege Defense**: Every case, suspect, and evidence request is authorized against the authenticated user's assignments and role.

---

## 2. Password Hashing & Brute-Force Lockout

### PBKDF2-HMAC-SHA256
- **Algorithm**: `PBKDF2` using `HMAC-SHA256` (Python `hashlib.pbkdf2_hmac`).
- **Iterations**: `100,000` iterations (meeting NIST SP 800-132 recommendations for key stretching).
- **Salt**: 16 cryptographically secure random bytes generated via `secrets.token_bytes(16)`.
- **Verification**: Evaluated using constant-time comparison (`hmac.compare_digest`) to prevent timing side-channel attacks.

### Sliding Window & Brute-Force Lockout
- **Rate Limiting**: Sliding window rate limiter enforcing maximum requests per minute per IP address.
- **Lockout Policy**: After `5` consecutive failed login attempts on a user account:
  - Account transitions to `LOCKED` state for `15 minutes` (`900` seconds).
  - Subsequent authentication attempts fail immediately with `403 Forbidden` (`Account locked due to consecutive failed attempts`).
  - Intruder snapshot and IP telemetry are logged to the tamper-evident audit trail.

---

## 3. Token Lifecycle: JWT & Refresh Token Rotation

### Access Tokens (HMAC-SHA256)
- **Format**: URL-safe base64-encoded standard three-part JWT (`header.payload.signature`).
- **Algorithm**: Enforces `HS256`. The verification pipeline explicitly checks that `alg == "HS256"` in the decoded header, rejecting `'none'` algorithm bypass attacks.
- **Lifespan**: Short-lived access tokens (`15 minutes` / `900 seconds`).
- **Claims**: Includes Subject ID (`sub`), Role (`role`), Badge (`badge`), Expiration (`exp`), Issued At (`iat`), and Token Use (`token_use="access"`).

### Refresh Token Rotation & Revocation
- **Storage**: Refresh tokens are stored in the SQLite `refresh_tokens` table keyed by their `SHA-256` digest (`token_hash`).
- **Rotation Rule**: When a refresh token is used to obtain a new access token via `/api/auth/refresh`:
  - The presenting token is validated and checked against `revoked == 0` and `expires_at > time()`.
  - The presented token is **immediately revoked** (`revoked = 1`).
  - A fresh access token and a brand new refresh token are issued.
- **Revocation on Logout**: Explicit `/api/auth/logout` revokes the refresh token hash immediately.

---

## 4. Role-Based Access Control (RBAC) & IDOR Prevention

### The 4 Role Tiers

| Role | Hierarchy Level | Permissions |
| :--- | :---: | :--- |
| `INTELLIGENCE_AUDITOR` | 1 | Read-only access to cases, reports, and evidence ledger. Denied evidence ingestion, alert review, or stage escalation. |
| `FORENSIC_ANALYST` | 2 | Case telemetry analysis, evidence uploading, initial alert review, and analytical query execution on assigned cases. |
| `LEAD_INVESTIGATOR` | 3 | Case assignment management, evidence handling, alert confirmation, stage advancement, and report drafting. |
| `SUPERVISORY_OFFICER` | 4 | Full jurisdiction oversight, unassigned case inspection, supervisor escalations, warrant review sign-off, and system settings. |

### Horizontal IDOR Defense
Every API route handling case resources enforces `require_case_access`:
1. If the requesting user holds the `SUPERVISORY_OFFICER` role, access is permitted across all cases for supervisory oversight.
2. For all other roles, the backend executes an explicit relational query:
   ```sql
   SELECT 1 FROM cases WHERE id = ? AND lead_investigator_id = ?
   UNION
   SELECT 1 FROM case_assignments WHERE case_id = ? AND user_id = ?
   ```
3. If no assignment record exists, the request fails immediately with `403 Forbidden: You are not assigned to this case.`

---

## 5. PII Encryption at Rest (AES-256-GCM)

Personally Identifiable Information (such as suspect phone numbers, home addresses, and financial account identifiers) is encrypted at rest using **NIST SP 800-38D AES-256-GCM**:
- **Key Size**: 256 bits (32 bytes).
- **Nonce / IV**: A fresh 96-bit (12-byte) cryptographically secure nonce (`os.urandom(12)`) is generated per encryption operation. Nonce reuse is mathematically prevented.
- **Authentication Tag**: 128-bit authentication tag appended to the ciphertext to detect any post-write corruption or bit-flipping.
- **Envelope Format**: `enc:v1:<nonce_b64>:<ciphertext_and_tag_b64>`.

---

## 6. Realtime WebSocket Authentication (Socket.IO)

Unlike legacy systems that leave WebSockets unauthenticated:
- The Socket.IO connection handshake requires a valid Bearer JWT passed in `auth.token` or query parameter.
- Connections without valid access tokens are disconnected during `connect`.
- Joining investigation rooms (`join_case_room`) checks that the connected user is assigned to `case_{case_id}` before granting subscription. Unauthorized clients receive `room_join_error` and are denied event telemetry.

---

## 7. Edge Biometrics Prototype Notice

CrimeNet AI includes an edge webcam verification module utilizing **Zero-Normalized Cross-Correlation (ZNCC)** with 7-frame multi-frame averaging:
- **Technical Status**: Clearly labeled as a **Client-Side Prototype / Demonstration**.
- **Limitations**: ZNCC on 2D video frames does not protect against high-resolution physical photo presentation attacks (liveness detection requires depth/IR sensors).
- **Production Defense**: Primary authentication relies on strong PBKDF2 passcodes and HMAC-SHA256 JWT tokens; biometric scoring serves as an auxiliary second-factor prototype.
