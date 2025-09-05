# server/models/db_models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "Users"
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Username = Column(String(50), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    password_hash = Column(String(255), nullable=False)        # existing column name
    role = Column(String(50), nullable=False, default="USER")   # USER/AGENT/ADMIN
    is_active = Column(Boolean, nullable=False, default=True)
    agent_status = Column(String(20), nullable=False, default="NONE")  # NONE/REQUESTED/APPROVED/REJECTED

    events = relationship("EventDB", back_populates="creator", cascade="all,delete-orphan")
    registrations = relationship("RegistrationDB", back_populates="user", cascade="all,delete-orphan")

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
    # new/updated fields we added in migration:
    starts_at = Column(DateTime)              # filled from old Date
    ends_at = Column(DateTime)
    status = Column(String(20), nullable=False, default="DRAFT")
    capacity = Column(Integer, nullable=False, default=0)
    description = Column(String)              # NVARCHAR(MAX) -> String works
    image_url = Column(String(300))

    # optional relation to creator (if you later add a CreatedBy column)
    CreatedBy = Column(Integer, ForeignKey("Users.Id"), nullable=True)
    creator = relationship("UserDB", back_populates="events", primaryjoin="UserDB.Id==EventDB.CreatedBy")

    registrations = relationship("RegistrationDB", back_populates="event", cascade="all,delete-orphan")

class RegistrationDB(Base):
    __tablename__ = "Registrations"
    Id = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey("Users.Id"), nullable=False)
    EventId = Column(Integer, ForeignKey("Events.Id"), nullable=False)
    status = Column(String(20), nullable=False, default="CONFIRMED")  # CONFIRMED/WAITLIST/CANCELLED
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserDB", back_populates="registrations")
    event = relationship("EventDB", back_populates="registrations")

class AgentRequestDB(Base):
    __tablename__ = "AgentRequests"
    Id = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey("Users.Id"), nullable=False)
    status = Column(String(20), nullable=False, default="NEW")  # NEW/APPROVED/REJECTED
    reason = Column(String(500))
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    DecidedAt = Column(DateTime)
    DecidedByUserId = Column(Integer, ForeignKey("Users.Id"))

class ReactionsDB(Base):
    __tablename__ = "Reactions"
    Id = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey("Users.Id"), nullable=False)
    EventId = Column(Integer, ForeignKey("Events.Id"), nullable=False)
    type = Column(String(10), nullable=False)  # LIKE | SAVE
    CreatedAt = Column(DateTime, default=datetime.utcnow)
