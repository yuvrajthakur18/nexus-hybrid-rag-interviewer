from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from app.core.config import settings


def create_access_token(subject: str, claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp())}
    if claims:
        payload.update(claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_access_token(token: str) -> str:
    """
    Returns the token subject (user_id).
    Raises jose errors on invalid tokens.
    """
    decoded = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    sub = decoded.get("sub")
    if not sub:
        raise ValueError("missing_sub")
    return str(sub)
