# server/repositories/users_repo.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pyodbc

from server.core.config import settings
from server.models.user import UserInDB, UserCreate

class UsersRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserInDB]: ...
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserInDB]: ...
    @abstractmethod
    def create(self, data: UserCreate, password_hash: str, role: str = "USER") -> UserInDB: ...

def _conn():
    # autocommit=True כדי למנוע צורך ב-commit ידני
    return pyodbc.connect(settings.DB_URL, autocommit=True)

def _row_to_user(row: Any) -> UserInDB:
    return UserInDB(
        id=int(row[0]),
        username=row[1],
        email=row[2],
        password_hash=row[3],
        role=(row[4] or "USER").upper(),
        is_active=bool(row[5]),
    )

class SqlUsersRepository(UsersRepository):
    def get_by_email(self, email: str) -> Optional[UserInDB]:
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT Id, Username, Email, password_hash, role, is_active "
                "FROM Users WHERE LOWER(Email) = LOWER(?)",
                (email.lower(),),
            )
            row = cur.fetchone()
        return _row_to_user(row) if row else None

    def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT Id, Username, Email, password_hash, role, is_active "
                "FROM Users WHERE Id = ?",
                (int(user_id),),
            )
            row = cur.fetchone()
        return _row_to_user(row) if row else None

    def create(self, data: UserCreate, password_hash: str, role: str = "USER") -> UserInDB:
        # מונע כפילות אימייל
        if self.get_by_email(data.email):
            raise ValueError("email already exists")

        with _conn() as conn:
            cur = conn.cursor()
            # שלב 1: INSERT (תואם לכל דרייבר; ללא OUTPUT)
            cur.execute(
                "INSERT INTO Users (Username, Email, password_hash, role) VALUES (?, ?, ?, ?)",
                (data.username.strip(), data.email.lower(), password_hash, role.upper()),
            )
            # שלב 2: שליפה חזרה לפי אימייל (מניחים ייחודיות אימייל)
            cur.execute(
                "SELECT Id, Username, Email, password_hash, role, is_active "
                "FROM Users WHERE LOWER(Email) = LOWER(?)",
                (data.email.lower(),),
            )
            row = cur.fetchone()

        if not row:
            # אם זה קורה — יש בעיית טרנזקציה/ODBC; עדיף להרים חריגה מאשר "להמשיך כרגיל"
            raise RuntimeError("Insert succeeded but no row returned")

        return _row_to_user(row)

class InMemoryUsersRepository(UsersRepository):
    def __init__(self) -> None:
        self._by_id: Dict[int, UserInDB] = {}
        self._by_email: Dict[str, int] = {}
        self._next_id = 1

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        uid = self._by_email.get(email.lower())
        return self._by_id.get(uid) if uid else None

    def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        return self._by_id.get(int(user_id))

    def create(self, data: UserCreate, password_hash: str, role: str = "USER") -> UserInDB:
        if self.get_by_email(data.email):
            raise ValueError("email already exists")
        uid = self._next_id
        self._next_id += 1
        user = UserInDB(
            id=uid,
            email=data.email.lower(),
            username=data.username.strip(),
            password_hash=password_hash,
            role=role.upper(),
            is_active=True,
        )
        self._by_id[uid] = user
        self._by_email[user.email] = uid
        return user

# בחירה ב-SQL או בזיכרון (עם לוג ברור — שלא תחשבי שהכול נשמר DB כשזה לא)
try:
    _ = _conn().cursor()
    repo_users: UsersRepository = SqlUsersRepository()
    print("[UsersRepository] Using SQL repository")
except Exception as e:
    print(f"[UsersRepository] Falling back to InMemory repository (DB error: {e})")
    repo_users = InMemoryUsersRepository()
