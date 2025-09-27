# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app import crud
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_admin, require_owner_or_admin
from app.models import User as UserModel


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # فقط ادمین
    require_admin(current_user)
    return crud.users.get_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # ادمین یا صاحب حساب
    require_owner_or_admin(current_user, resource_owner_id=user_id)
    u = crud.users.get_user(db, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u


# نکته: ساخت کاربر از طریق /auth/register انجام می‌شود.
# اگر نیاز داری ادمین از اینجا هم کاربر بسازد، این متد را از کامنت خارج کن.

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    require_admin(current_user)
    exists = crud.users.get_user_by_email(db, payload.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.users.create_user(db, payload)



@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserCreate,  # در مدل تو Full update با UserCreate بود؛ اگر خواستی می‌تونیم جداگانه UserUpdateFull بسازیم
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # ادمین یا صاحب حساب
    require_owner_or_admin(current_user, resource_owner_id=user_id)
    u = crud.users.update_user(db, user_id, payload)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u


@router.patch("/{user_id}", response_model=UserOut)
def patch_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # ادمین یا صاحب حساب
    require_owner_or_admin(current_user, resource_owner_id=user_id)
    u = crud.users.patch_user(db, user_id, payload)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # ادمین یا صاحب حساب (اگر حذف کاربر را فقط ادمین می‌خواهی، اینجا require_admin(current_user) بگذار)
    require_owner_or_admin(current_user, resource_owner_id=user_id)
    ok = crud.users.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return None
