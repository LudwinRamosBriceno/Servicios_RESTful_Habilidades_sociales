import os
import secrets
import threading
import time
from typing import Any

# Almacen en memoria para sesiones (se pierde si el servicio se reinicia).
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "auth_session")
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))

_sessions: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()


def _now_seconds() -> int:
    return int(time.time())


def _purge_if_expired(session_id: str, session: dict[str, Any]) -> bool:
    if session.get("expires_at", 0) <= _now_seconds():
        _sessions.pop(session_id, None)
        return True
    return False


def create_session(user_id: str, name: str | None) -> tuple[str, int]:
    session_id = secrets.token_urlsafe(32)
    expires_at = _now_seconds() + SESSION_TTL_SECONDS
    with _lock:
        _sessions[session_id] = {
            "user_id": user_id,
            "name": name,
            "expires_at": expires_at,
        }
    return session_id, expires_at


def get_session(session_id: str | None) -> dict[str, Any] | None:
    if not session_id:
        return None
    with _lock:
        session = _sessions.get(session_id)
        if not session:
            return None
        if _purge_if_expired(session_id, session):
            return None
        return dict(session)


def delete_session(session_id: str | None) -> None:
    if not session_id:
        return
    with _lock:
        _sessions.pop(session_id, None)
