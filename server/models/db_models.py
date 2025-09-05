from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Float, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum
from uuid import uuid4
from sqlalchemy import Index

Base = declarative_base()

# --- ENUMS ---
class RoleEnum(str, enum.Enum):
    USER = "USER"
    AGENT = "AGENT"
    ADMIN = "ADMIN"

class AgentStatusEnum(str, enum.Enum):
    NONE = "NONE"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class EventStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"

class RegistrationStatusEnum(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    WAITLIST = "WAITLIST"
    CANCELLED = "CANCELLED"


# --- MODELS ---
class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: uuid4().hex)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    agent_status = Column(Enum(AgentStatusEnum), default=AgentStatusEnum.NONE, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    events = relationship("EventDB", back_populates="creator")
    registrations = relationship("RegistrationDB", back_populates="user")


class EventDB(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: uuid4().hex)
    title = Column(String, nullable=False)
    category = Column(String, nullable=True)
    location = Column(String, nullable=True)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=True)
    status = Column(Enum(EventStatusEnum), default=EventStatusEnum.PUBLISHED, nullable=False)
    capacity = Column(Integer, nullable=False, default=0)
    image_url = Column(String, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    creator = relationship("UserDB", back_populates="events")
    registrations = relationship("RegistrationDB", back_populates="event")


class RegistrationDB(Base):
    __tablename__ = "registrations"

    id = Column(String, primary_key=True, default=lambda: uuid4().hex)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    status = Column(Enum(RegistrationStatusEnum), nullable=False, default=RegistrationStatusEnum.CONFIRMED)
    quantity = Column(Integer, default=1)
    total_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_user_event"),)

    # relationships
    user = relationship("UserDB", back_populates="registrations")
    event = relationship("EventDB", back_populates="registrations")


class AgentRequestDB(Base):
    __tablename__ = "agent_requests"

    id = Column(String, primary_key=True, default=lambda: uuid4().hex)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    reason = Column(String, nullable=False)
    status = Column(Enum(AgentStatusEnum), default=AgentStatusEnum.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)
    decided_by = Column(String, ForeignKey("users.id"), nullable=True)

Index("ix_events_status_start", EventDB.status, EventDB.starts_at)
Index("ix_regs_event_status", RegistrationDB.event_id, RegistrationDB.status)