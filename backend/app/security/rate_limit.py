import time
from typing import Dict, List, Tuple
from collections import defaultdict
from backend.app.config import MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION_SECONDS

# IP-based sliding window rate limiter
_REQUEST_TIMESTAMPS: Dict[str, List[float]] = defaultdict(list)

# Account & IP lockout trackers
_FAILED_ATTEMPTS: Dict[str, int] = defaultdict(int)
_LOCKOUT_TIMESTAMPS: Dict[str, float] = {}

def check_rate_limit(client_ip: str, max_requests: int = 120, window_seconds: int = 60) -> bool:
    """Sliding-window rate limiter per client IP. Returns True if allowed, False if exceeded."""
    now = time.time()
    cutoff = now - window_seconds
    timestamps = _REQUEST_TIMESTAMPS[client_ip]
    # Prune old timestamps
    _REQUEST_TIMESTAMPS[client_ip] = [ts for ts in timestamps if ts > cutoff]
    
    if len(_REQUEST_TIMESTAMPS[client_ip]) >= max_requests:
        return False
        
    _REQUEST_TIMESTAMPS[client_ip].append(now)
    return True

def is_account_locked(identifier: str) -> Tuple[bool, int]:
    """Checks if an account or IP is currently locked out. Returns (is_locked, remaining_seconds)."""
    now = time.time()
    lockout_until = _LOCKOUT_TIMESTAMPS.get(identifier, 0)
    if lockout_until > now:
        remaining = int(lockout_until - now)
        return True, remaining
    return False, 0

def record_failed_login(identifier: str) -> Tuple[int, bool]:
    """Records a failed login attempt. If threshold exceeded, triggers lockout.
    Returns (attempt_count, newly_locked).
    """
    _FAILED_ATTEMPTS[identifier] += 1
    attempts = _FAILED_ATTEMPTS[identifier]
    if attempts >= MAX_LOGIN_ATTEMPTS:
        _LOCKOUT_TIMESTAMPS[identifier] = time.time() + LOCKOUT_DURATION_SECONDS
        return attempts, True
    return attempts, False

def reset_failed_logins(identifier: str):
    """Resets failed login counters upon successful authentication."""
    if identifier in _FAILED_ATTEMPTS:
        del _FAILED_ATTEMPTS[identifier]
    if identifier in _LOCKOUT_TIMESTAMPS:
        del _LOCKOUT_TIMESTAMPS[identifier]
