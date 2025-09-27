from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import Token
from app.crud import users
from app.crud.tokens import revoke_token
from app.database.session import get_db
from app.auth.hashing import verify_password
from app.auth.jwt_handler import (
    create_access_token, create_refresh_token,
    decode_refresh_token, decode_access_token
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    db_user = users.get_user_by_email(db, payload.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return users.create_user(db, payload)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = users.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    acc = create_access_token(sub=user.email, role=user.role.value if hasattr(user.role, "value") else str(user.role))
    ref = create_refresh_token(sub=user.email, role=user.role.value if hasattr(user.role, "value") else str(user.role))
    return {"access_token": acc["token"], "refresh_token": ref["token"], "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # اگر این رفرش قبلاً باطل شده باشد، اجازه نده
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    from app.crud.tokens import is_token_revoked
    if is_token_revoked(db, jti):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    # توکن جدید بساز و رفرش فعلی را rotation کنیم (باطل کنیم)
    email = payload.get("sub")
    role = payload.get("role")
    acc = create_access_token(sub=email, role=role)
    new_ref = create_refresh_token(sub=email, role=role)

    # رفرش قبلی را باطل کن (Rotation)
    from datetime import datetime, timezone
    exp_ts = payload.get("exp")
    exp_dt = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
    revoke_token(db, jti=jti, token_type="refresh", expires_at=exp_dt)

    return {"access_token": acc["token"], "refresh_token": new_ref["token"], "token_type": "bearer"}


@router.post("/logout", status_code=204)
def logout(request: Request, db: Session = Depends(get_db)):
    """
    لاگ‌اوت: توکن access فعلی را از هدر Authorization بردار و باطل کن.
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = auth.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    # باطل‌سازی (Blacklist)
    from datetime import datetime, timezone
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=401, detail="Invalid token")
    exp_ts = payload.get("exp")
    exp_dt = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
    revoke_token(db, jti=jti, token_type="access", expires_at=exp_dt)
    return None


@router.post("/logout_all", status_code=204)
def logout_all(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    لاگ‌اوت کامل: رفرش‌توکن فعلی را باطل می‌کنیم.
    با این کار، عملاً سشن کاربر خاتمه می‌یابد.
    """
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    from datetime import datetime, timezone
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    exp_ts = payload.get("exp")
    exp_dt = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
    revoke_token(db, jti=jti, token_type="refresh", expires_at=exp_dt)
    return None

