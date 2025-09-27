from datetime import datetime, timedelta, timezone
from jose import jwt
import os
import uuid
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


def _utcnow():
    return datetime.now(timezone.utc)


def _encode(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    exp = _utcnow() + expires_delta
    jti = str(uuid.uuid4())
    to_encode.update({"exp": exp, "jti": jti})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(sub: str, role: str) -> dict:
    """
    خروجی: dict با خود token + exp + jti
    """
    exp_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = _encode({"sub": sub, "role": role, "type": "access"}, exp_delta)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return {"token": token, "exp": datetime.fromtimestamp(payload["exp"], tz=timezone.utc), "jti": payload["jti"]}

def create_refresh_token(sub: str, role: str) -> dict:
    exp_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    token = _encode({"sub": sub, "role": role, "type": "refresh"}, exp_delta)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return {"token": token, "exp": datetime.fromtimestamp(payload["exp"], tz=timezone.utc), "jti": payload["jti"]}

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except Exception:
        return None

def decode_refresh_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except Exception:
        return None
