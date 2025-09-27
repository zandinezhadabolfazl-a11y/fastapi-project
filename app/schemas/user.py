from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


# 🎭 نقش‌های کاربر (Role)
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


# 🧱 پایه: چیزهایی که همه مدل‌ها مشترک دارن
class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="نام کامل کاربر")
    age: int = Field(..., ge=5, le=120, description="سن کاربر (۵ تا ۱۲۰)")
    email: EmailStr = Field(..., description="ایمیل معتبر کاربر")


# 🆕 برای ثبت‌نام
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="پسورد حداقل ۸ کاراکتر")
    role: Optional[UserRole] = Field(
        default=UserRole.USER,
        description="نقش کاربر (user یا admin)، پیش‌فرض user"
    )


# 📝 برای بروزرسانی
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    age: Optional[int] = Field(None, ge=5, le=120)
    role: Optional[UserRole] = Field(None, description="تغییر نقش کاربر")


# 📤 خروجی API (نمایش به کاربر)
class UserOut(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Ali Reza",
                "age": 25,
                "email": "ali@example.com",
                "role": "user"
            }
        }
