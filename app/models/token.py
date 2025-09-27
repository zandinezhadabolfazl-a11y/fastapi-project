from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.base import Base

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False)   # ⚠️ index=True رو حذف کن
    token_type = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
