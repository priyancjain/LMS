import base64
import hashlib
import hmac
import json
import os
import secrets
import ssl
import urllib.error
import urllib.parse
import urllib.request

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter()

SESSION_COOKIE_NAME = "adaptive_poc_session"
TEACHER_EMAIL = "jnpriyanshipragya@gmail.com"

# For development: Create SSL context that doesn't verify certificates
# TODO: Remove this in production and use proper certificates
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise HTTPException(status_code=500, detail=f"Missing environment variable: {name}")
    return value


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(raw: str) -> bytes:
    padded = raw + "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _sign(payload: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
    return _b64url_encode(digest)


def _encode_session(data: dict, secret: str) -> str:
    payload = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = _b64url_encode(payload)
    sig_b64 = _sign(payload, secret)
    return f"{payload_b64}.{sig_b64}"


def _decode_session(token: str, secret: str) -> dict:
    try:
        payload_b64, sig_b64 = token.split(".", 1)
        payload = _b64url_decode(payload_b64)
        expected_sig_b64 = _sign(payload, secret)
        if not hmac.compare_digest(expected_sig_b64, sig_b64):
            return {}
        data = json.loads(payload.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _get_session(request: Request) -> dict:
    secret = _require_env("SESSION_SECRET")
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return {}
    return _decode_session(token, secret)


def _set_session_cookie(response, data: dict) -> None:
    secret = _require_env("SESSION_SECRET")
    token = _encode_session(data, secret)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
    )


def set_session(response, data: dict) -> None:
    _set_session_cookie(response, data)


def get_session(request: Request) -> dict:
    return _get_session(request)


def resolve_role(email: str) -> str:
    if email == TEACHER_EMAIL:
        return "teacher"
    return "student"


def require_role(required_role: str):
    def _dependency(request: Request) -> dict:
        session = _get_session(request)
        role = session.get("role")
        if not session.get("email") or role != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return session

    return _dependency


def _google_authorize_url(redirect_uri: str, state: str) -> str:
    client_id = _require_env("GOOGLE_CLIENT_ID")
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email",
        "state": state,
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)


def _exchange_code_for_token(code: str, redirect_uri: str) -> str:
    client_id = _require_env("GOOGLE_CLIENT_ID")
    client_secret = _require_env("GOOGLE_CLIENT_SECRET")

    form = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10, context=_ssl_context) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8")
        print(f"Google token exchange error: {error_body}")
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {error_body}") from exc
    except Exception as exc:
        print(f"Token exchange exception: {exc}")
        raise HTTPException(status_code=400, detail="Token exchange failed") from exc

    access_token = payload.get("access_token")
    if not access_token:
        error_details = payload.get("error_description", payload.get("error", "Unknown error"))
        print(f"No access token in response: {payload}")
        raise HTTPException(status_code=400, detail=f"No access_token returned by Google: {error_details}")
    return access_token


def _fetch_user_email(access_token: str) -> str:
    req = urllib.request.Request(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10, context=_ssl_context) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Failed to fetch user profile") from exc

    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="No email returned by Google")
    return email


@router.get("/login/google")
def login_google(request: Request):
    # Generate redirect URI with proper HTTPS handling
    # On Render, X-Forwarded-Proto header tells us the original protocol
    protocol = request.headers.get("X-Forwarded-Proto", "https")
    host = request.headers.get("Host", request.url.netloc)
    
    redirect_uri = f"{protocol}://{host}/auth/callback"
    
    print(f"DEBUG: redirect_uri = {redirect_uri}")
    print(f"DEBUG: protocol = {protocol}")
    print(f"DEBUG: host = {host}")
    
    state = secrets.token_urlsafe(24)

    session = _get_session(request)
    session["oauth_state"] = state

    response = RedirectResponse(url=_google_authorize_url(redirect_uri, state))
    _set_session_cookie(response, session)
    return response


@router.get("/auth/callback", name="auth_callback")
def auth_callback(request: Request, code: str | None = None, state: str | None = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    session = _get_session(request)
    expected_state = session.get("oauth_state")
    if not expected_state or not state or state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid state")

    # Generate redirect URI with proper HTTPS handling
    # On Render, X-Forwarded-Proto header tells us the original protocol
    protocol = request.headers.get("X-Forwarded-Proto", "https")
    host = request.headers.get("Host", request.url.netloc)
    
    redirect_uri = f"{protocol}://{host}/auth/callback"
    
    print(f"DEBUG: callback redirect_uri = {redirect_uri}")
    print(f"DEBUG: callback protocol = {protocol}")
    print(f"DEBUG: callback host = {host}")
    
    access_token = _exchange_code_for_token(code, redirect_uri)
    email = _fetch_user_email(access_token)

    session.pop("oauth_state", None)
    session["email"] = email
    session["role"] = resolve_role(email)

    dashboard_path = "/teacher/dashboard" if session["role"] == "teacher" else "/student/dashboard"
    response = RedirectResponse(url=dashboard_path)
    _set_session_cookie(response, session)
    return response
