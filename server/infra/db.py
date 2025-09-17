# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Server — infra/db.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
Create a SQLAlchemy Engine and Session factory.
Supports:
- Full SQLAlchemy URLs (e.g., sqlite:///..., postgresql+psycopg://...)
- Raw ODBC connection strings for SQL Server (Somee). These are
  URL-encoded automatically into mssql+pyodbc:///?odbc_connect=...
"""

from __future__ import annotations

import urllib.parse
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.core.config import settings


def _build_sqlalchemy_url(raw: str) -> str:
    """
    Build a SQLAlchemy URL from either:
      - a full SQLAlchemy URL (contains '://'), OR
      - a raw ODBC connection string (Driver=...;Server=...;Uid=...;Pwd=...).
    """
    s = (raw or "").strip()

    # If developer already provided a full SQLAlchemy URL, just use it.
    # Examples: sqlite:///./eventhub.db, postgresql+psycopg://user:pass@host/db
    if "://" in s and not s.lower().startswith("mssql+pyodbc:///?odbc_connect="):
        return s

    # Special-case SQLite shorthand (optional)
    if s.lower().startswith("sqlite"):
        return s

    # Otherwise, assume it is a raw ODBC connection string → encode for pyodbc
    # Example raw ODBC (Somee / SQL Server):
    #   Driver={ODBC Driver 17 for SQL Server};Server=tcp:your.somee.com;
    #   Database=YourDb;Uid=YourUser;Pwd=YourPass;Encrypt=yes;TrustServerCertificate=no;
    odbc_encoded = urllib.parse.quote_plus(s)
    return f"mssql+pyodbc:///?odbc_connect={odbc_encoded}"


SQLALCHEMY_URL = _build_sqlalchemy_url(settings.DB_URL)

engine = create_engine(
    SQLALCHEMY_URL,
    pool_pre_ping=True,                      # avoid stale connections
    echo=(settings.ENV.lower() != "production"),
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def get_db() -> Generator:
    """
    FastAPI dependency:
        from fastapi import Depends
        def endpoint(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
