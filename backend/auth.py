"""
EchoAid authentication helpers.

Provides PIN verification and signed JWT session token creation/validation.
Tokens are delivered as HTTP-only cookies so the secret never reaches the browser.
"""

import datetime

from fastapi import Cookie, HTTPException, status
from jose import JWTError, jwt

from backend.config import settings

ALGORITHM = "HS256"
TOKEN_COOKIE = "echoaid_session"


def create_session_token() -> str:
    """Create a signed JWT that acts as the guardian session token."""
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=settings.session_expire_minutes
    )
    payload = {"sub": "guardian", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def verify_session_token(token: str) -> bool:
    """Return True if the token is valid and not expired."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("sub") == "guardian"
    except JWTError:
        return False


def require_guardian(echoaid_session: str = Cookie(default=None)) -> None:
    """
    FastAPI dependency — raises 401 if the guardian session cookie is missing
    or invalid.  Use as:

        @router.get("/protected")
        def protected(auth=Depends(require_guardian)):
            ...
    """
    if not echoaid_session or not verify_session_token(echoaid_session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Guardian authentication required.",
        )
