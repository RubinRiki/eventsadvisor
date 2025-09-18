# server/infra/db.py
from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.core.config import settings

# engine_kwargs = dict(pool_pre_ping=True)

# engine = create_engine(settings.DB_URL, **engine_kwargs)

engine_kwargs = dict(
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=5,          
)

engine = create_engine(
    settings.DB_URL,
    connect_args={"timeout": 5},
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
