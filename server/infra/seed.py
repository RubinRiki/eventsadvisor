# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Server — infra/seed.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
Minimal seed script to ensure DB tables exist.

What it does now:
- Imports SQLAlchemy Base from your models module.
- Calls Base.metadata.create_all(engine) to create tables safely.

Why minimal?
- Until we verify model names and relations, we avoid inserting demo data.
  We'll add initial demo rows (users, events, registrations) after we confirm models.

Run:
    python -m server.infra.seed
"""

from __future__ import annotations

from server.infra.db import engine

# We try a few common locations for Base to keep this script flexible.
Base = None
try:
    # Most likely path (e.g., db_models.py defines `Base = declarative_base()`):
    from server.models.db_models import Base as _Base

    Base = _Base
except Exception:
    try:
        # Alternative: models/__init__.py exposes `Base`
        from server.models import Base as _Base

        Base = _Base
    except Exception:
        raise ImportError(
            "Could not import SQLAlchemy Base. "
            "Make sure your models module exposes `Base` "
            "(e.g., in server/models/db_models.py or server/models/__init__.py)."
        )


def main() -> None:
    # Create all tables if they do not exist yet
    Base.metadata.create_all(bind=engine)
    print("✅ DB schema ensured (create_all completed).")


if __name__ == "__main__":
    main()
