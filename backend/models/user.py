"""
User model for authentication.
"""

from uuid import UUID
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func

from backend.models.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"