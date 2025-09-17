# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Server — models/db_models.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
SQLAlchemy ORM models for the EventHub backend.

Highlights:
- Keeps existing column names (PascalCase/snake_case) to avoid breaking code.
- Adds relationships for Reactions (user/event).
- Adds useful DB constraints and indexes to prevent duplicates and speed up queries.
- Uses Text for long descriptions (friendly for SQL Server NVARCHAR(MAX)).
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Numeric,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# -----------------------------
# Users
# -----------------------------
class UserDB(Base):
    __tablename__ = "Users"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Username = Column(String(50), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="USER")  # USER/AGENT/ADMIN
    is_active = Column(Boolean, nullable=False, default=True)
    agent_status = Column(String(20), nullable=False, default="NONE")  # NONE/REQUESTED/APPROVED/REJECTED

    # Relationships
    events = relationship("EventDB", back_populates="creator", cascade="all,delete-orphan")
    registrations = relationship("RegistrationDB", back_populates="user", cascade="all,delete-orphan")
    reactions = relationship("ReactionsDB", back_populates="user", cascade="all,delete-orphan")

    def __repr__(self) -> str:
        return f"<UserDB Id={self.Id} Email={self.Email} Role={self.role}>"


# -----------------------------
# Events
# -----------------------------
class EventDB(Base):
    __tablename__ = "Events"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Title = Column(String(200), nullable=False)
    Category = Column(String(100))
    Venue = Column(String(200))
    City = Column(String(100))
    Country = Column(String(50))
    Url = Column(String(300))
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    Price = Column(Numeric(10, 2))

    # New/updated fields
    starts_at = Column(DateTime)  # migrated from old Date
    ends_at = Column(DateTime)
    status = Column(String(20), nullable=False, default="DRAFT")
    capacity = Column(Integer, nullable=False, default=0)
    description = Column(Text)  # NVARCHAR(MAX) equivalent on MSSQL
    image_url = Column(String(300))

    # Optional relation to creator
    CreatedBy = Column(Integer, ForeignKey("Users.Id", ondelete="SET NULL"), nullable=True)
    creator = relationship("UserDB", back_populates="events", primaryjoin="UserDB.Id==EventDB.CreatedBy")

    # Relationships
    registrations = relationship("RegistrationDB", back_populates="event", cascade="all,delete-orphan")
    reactions = relationship("ReactionsDB", back_populates="event", cascade="all,delete-orphan")

    # Helpful indexes for search
    __table_args__ = (
        Index("ix_events_category", "Category"),
        Index("ix_events_city", "City"),
        Index("ix_events_starts_at", "starts_at"),
    )

    def __repr__(self) -> str:
        return f"<EventDB Id={self.Id} Title={self.Title} City={self.City}>"


# -----------------------------
# Registrations
# -----------------------------
class RegistrationDB(Base):
    __tablename__ = "Registrations"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey("Users.Id", ondelete="CASCADE"), nullable=False)
    EventId = Column(Integer, ForeignKey("Events.Id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="CONFIRMED")  # CONFIRMED/WAITLIST/CANCELLED
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserDB", back_populates="registrations")
    event = relationship("EventDB", back_populates="registrations")

    # One registration per user per event
    __table_args__ = (
        UniqueConstraint("UserId", "EventId", name="uq_reg_user_event"),
    )

    def __repr__(self) -> str:
        return f"<RegistrationDB Id={self.Id} UserId={self.UserId} EventId={self.EventId} Status={self.status}>"


# -----------------------------
# Agent Requests
# -----------------------------
class AgentRequestDB(Base):
    __tablename__ = "AgentRequests"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey("Users.Id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="NEW")  # NEW/APPROVED/REJECTED
    reason = Column(String(500))
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    DecidedAt = Column(DateTime)
    DecidedByUserId = Column(Integer, ForeignKey("Users.Id"))

    def __repr__(self) -> str:
        return f"<AgentRequestDB Id={self.Id} UserId={self.UserId} Status={self.status}>"


# -----------------------------
# Reactions (LIKE/SAVE)
# -----------------------------
class ReactionsDB(Base):
    __tablename__ = "Reactions"

    Id = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey("Users.Id", ondelete="CASCADE"), nullable=False)
    EventId = Column(Integer, ForeignKey("Events.Id", ondelete="CASCADE"), nullable=False)
    type = Column(String(10), nullable=False)  # LIKE | SAVE
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("UserDB", back_populates="reactions")
    event = relationship("EventDB", back_populates="reactions")

    # Prevent duplicate like/save for same user & event
    __table_args__ = (
        UniqueConstraint("UserId", "EventId", "type", name="uq_react_user_event_type"),
    )

    def __repr__(self) -> str:
        return f"<ReactionsDB Id={self.Id} UserId={self.UserId} EventId={self.EventId} Type={self.type}>"
