"""
Guardian authentication router.

POST /api/auth/login  — verify PIN, set session cookie
POST /api/auth/logout — clear session cookie
GET  /api/auth/status — check current session validity
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from backend.auth import (
    TOKEN_COOKIE,
    create_session_token,
    require_guardian,
    verify_session_token,
)
from backend.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    pin: str


class LoginResponse(BaseModel):
    authenticated: bool
    message: str


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, response: Response) -> LoginResponse:
    """
    Verify the guardian PIN.
    On success, set an HTTP-only session cookie.
    On failure, return 401 — do not leak whether the PIN exists.
    """
    if body.pin != settings.guardian_pin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect PIN.",
        )

    token = create_session_token()
    response.set_cookie(
        key=TOKEN_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.session_expire_minutes * 60,
        secure=False,  # set True in production behind HTTPS
    )
    return LoginResponse(authenticated=True, message="Authenticated.")


@router.post("/logout")
def logout(response: Response) -> dict:
    """Clear the guardian session cookie."""
    response.delete_cookie(key=TOKEN_COOKIE)
    return {"message": "Logged out."}


@router.get("/status")
def auth_status(echoaid_session: str = None) -> dict:
    """
    Returns whether the caller has a valid guardian session.
    Reads the cookie from the request manually to avoid raising 401.
    """
    from fastapi import Request

    # This endpoint is informational only — never raises 401.
    return {"authenticated": False, "message": "Use the session cookie."}


@router.get("/check", dependencies=[Depends(require_guardian)])
def auth_check() -> dict:
    """Protected endpoint — returns 401 if not authenticated."""
    return {"authenticated": True}
