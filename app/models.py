from datetime import datetime, UTC
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Uuid, func
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='user')

    user_info = relationship("UserInfo", back_populates="user", uselist=False, cascade="all, delete-orphan")
    items = relationship("Item", back_populates="owner")
    session = relationship("UserSession", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserInfo(Base):
    __tablename__ = "user_infos"

    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    designation = Column(String)
    staff_id = Column(Integer, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("User", back_populates="user_info")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(Uuid, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    created_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime(), default=datetime.now(), onupdate=func.now())

    user = relationship("User", back_populates="session")