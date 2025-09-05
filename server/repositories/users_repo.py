# server/repositories/users_repo.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pyodbc
from server.models.user import User, UserCreate
from server.core.config import settings

# ---------- Contract ----------
class UsersRepository(ABC):
    """Abstract base class defining the user repository contract."""

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]: ...
    @abstractmethod
    def create(self, data: UserCreate, hashed_password: str, role: str = "user") -> User: ...


# ---------- Helpers ----------
def _conn():
    """Create and return a new database connection using pyodbc."""
    return pyodbc.connect(settings.DB_URL, autocommit=True)

def _row_to_user(row: Any) -> User:
    """Map a database row tuple into a User Pydantic model."""
    return User(
        id=str(row[0]),
        username=row[1],
        email=row[2],
        hashed_password=row[3],
        role=row[4],
        is_active=bool(row[5]),
    )


# ---------- SQL implementation ----------
class SqlUsersRepository(UsersRepository):
    """SQL Server implementation of the UsersRepository."""

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email (case-insensitive)."""
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, Username, email, password_hash, role, is_active FROM Users WHERE email = ?",
                (email.lower(),)
            )
            row = cur.fetchone()
        return _row_to_user(row) if row else None

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Fetch a user by primary key (Id)."""
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, Username, email, password_hash, role, is_active FROM Users WHERE id = ?",
                (user_id,)
            )
            row = cur.fetchone()
        return _row_to_user(row) if row else None

    def create(self, data: UserCreate, hashed_password: str, role: str = "user") -> User:
        """
        Insert a new user into the database.
        - Validates that the email does not already exist.
        - Relies on DB defaults for CreatedAt, role, and is_active.
        """
        if self.get_by_email(data.email):
            raise ValueError("email already exists")

        email = data.email.lower()
        username = data.username.strip()

        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO Users (Username, Email, password_hash)
                OUTPUT INSERTED.Id, INSERTED.Username, INSERTED.Email, INSERTED.password_hash, INSERTED.role, INSERTED.is_active
                VALUES (?, ?, ?)
                """,
                (username, email, hashed_password)
            )
            row = cur.fetchone()
        return _row_to_user(row)


# ---------- In-memory implementation ----------
class InMemoryUsersRepository(UsersRepository):
    """Simple in-memory implementation for local testing or fallback."""

    def __init__(self) -> None:
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, str] = {}

    def get_by_email(self, email: str) -> Optional[User]:
        """Return a user if the email exists in memory."""
        uid = self._by_email.get(email.lower())
        return self._by_id.get(uid) if uid else None

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Return a user by ID from the in-memory store."""
        return self._by_id.get(user_id)

    def create(self, data: UserCreate, hashed_password: str, role: str = "user") -> User:
        """
        Create a user in memory.
        Note: does not check for username uniqueness (only email).
        """
        from uuid import uuid4
        if self.get_by_email(data.email):
            raise ValueError("email already exists")

        uid = str(uuid4())
        user = User(
            id=uid,
            email=data.email.lower(),
            username=data.username,  # This will fail if User model requires username but not passed here
            hashed_password=hashed_password,
            role=role,
            is_active=True
        )
        self._by_id[uid] = user
        self._by_email[user.email] = uid
        return user


# ---------- Default repository ----------
try:
    # Smoke test for DB connection: if succeeds, use SQL Server repo
    _ = _conn().cursor()
    repo_users: UsersRepository = SqlUsersRepository()
except Exception:
    # If DB connection fails, fall back to in-memory repo
    repo_users = InMemoryUsersRepository()
