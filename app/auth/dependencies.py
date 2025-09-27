from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.crud import users
from app.crud.tokens import is_token_revoked
from app.auth.jwt_handler import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    jti = payload.get("jti")
    if not jti or is_token_revoked(db, jti):
        # این توکن قبلاً باطل شده یا مشکل دارد
        raise credentials_exception

    email: str = payload.get("sub")
    role: str = payload.get("role")
    if email is None or role is None:
        raise credentials_exception

    user = users.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user

def get_current_admin(current_user = Depends(get_current_user)):
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )
    return current_user
