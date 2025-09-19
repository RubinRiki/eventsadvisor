# server/repositories/users_repo.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
import os
import re
import urllib.parse
import pyodbc

from server.core.config import settings
from server.models.user import UserInDB, UserCreate

# =========================
# Errors (mapped, harmless up the stack)
# =========================
class RepoError(Exception):
    pass

class DuplicateEmailError(RepoError):
    pass

class DuplicateUsernameError(RepoError):
    pass

class NotFoundError(RepoError):
    pass


# =========================
# Normalizers
# =========================
def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()

def _normalize_username(username: str) -> str:
    v = (username or "").strip()
    return v or "user"

def _normalize_role(role: str) -> str:
    r = (role or "USER").strip().upper()
    return r if r in ("USER", "ADMIN") else "USER"


# =========================
# Connection helpers
# =========================
def _list_sql_drivers() -> list[str]:
    return [d for d in pyodbc.drivers() if "SQL Server" in d]

def _pick_installed_sql_driver() -> str:
    drivers = _list_sql_drivers()
    for pref in ("ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"):
        if pref in drivers:
            return pref
    return drivers[0] if drivers else "ODBC Driver 18 for SQL Server"

def _sqlalchemy_url_to_odbc_connstr(url: str, encrypt_default: str = "no") -> str:
    """
    Convert:
      1) mssql+pyodbc://USER:PASS@HOST/DB?driver=ODBC+Driver+18+for+SQL+Server
      2) mssql+pyodbc:///?odbc_connect=<percent-encoded-odbc-connstr>
    into a proper ODBC connstring for pyodbc.connect().
    """
    s = url.strip()

    # (2) odc_connect form
    m2 = re.match(r"^mssql\+pyodbc:///\?odbc_connect=(?P<enc>.+)$", s, flags=re.IGNORECASE)
    if m2:
        decoded = urllib.parse.unquote_plus(m2.group("enc"))
        return _normalize_connstr_driver(decoded)

    # (1) user:pass@host/db form
    m = re.match(
        r"^mssql\+pyodbc://(?P<user>[^:@]+):(?P<pwd>[^@]+)@(?P<host>[^/]+)/(?P<db>[^?]+)(?:\?(.+))?$",
        s,
        flags=re.IGNORECASE,
    )
    if not m:
        return s  # not a sqlalchemy url -> maybe already ODBC
    user, pwd, host, db = m.group("user"), m.group("pwd"), m.group("host"), m.group("db")

    # driver from query if present
    q = s.split("?", 1)[1] if "?" in s else ""
    driver = None
    for part in q.split("&"):
        if part.lower().startswith("driver="):
            driver = part.split("=", 1)[1].replace("+", " ").strip()
            break
    driver = driver or _pick_installed_sql_driver()

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={host};DATABASE={db};UID={user};PWD={pwd};"
        f"Encrypt={encrypt_default};TrustServerCertificate=yes;Connection Timeout=30"
    )

def _get_raw_db_url() -> str:
    """
    Prefer ENV (pure ODBC) first, then settings.DB_URL (SQLAlchemy URL resolved in config.py).
    """
    candidates = [
        os.getenv("EVENTHUB_DATABASE_URL"),
        os.getenv("EVENTHUB_DB_URL"),
        getattr(settings, "DB_URL", None),
        getattr(settings, "DATABASE_URL", None),
    ]
    for c in candidates:
        if c and str(c).strip():
            return str(c).strip()
    raise RepoError("No DB URL found. Use .env (EVENTHUB_DATABASE_URL / EVENTHUB_DB_URL) or settings.DB_URL.")

def _normalize_connstr_driver(connstr: str) -> str:
    """If requested driver isn't installed – switch to an installed one."""
    drivers = _list_sql_drivers()
    if not drivers:
        return connstr
    m = re.search(r"DRIVER=\{(?P<drv>[^}]+)\}", connstr, flags=re.IGNORECASE)
    if not m:
        return f"DRIVER={{{_pick_installed_sql_driver()}}};" + connstr
    requested = m.group("drv")
    if requested not in drivers:
        good = _pick_installed_sql_driver()
        connstr = re.sub(r"DRIVER=\{[^}]+\}", f"DRIVER={{{good}}}", connstr, flags=re.IGNORECASE)
    return connstr

def _build_connstr() -> str:
    raw = _get_raw_db_url()
    if "DRIVER=" in raw.upper():           # already ODBC connstring
        connstr = _normalize_connstr_driver(raw)
    else:                                   # mssql+pyodbc URL (both forms handled)
        connstr = _sqlalchemy_url_to_odbc_connstr(raw, encrypt_default="no")
        connstr = _normalize_connstr_driver(connstr)
    return connstr

def _conn() -> pyodbc.Connection:
    """
    Open pyodbc connection with autocommit.
    Raise RepoError with a clear hint if connection fails.
    """
    connstr = _build_connstr()
    try:
        return pyodbc.connect(connstr, autocommit=True)
    except pyodbc.Error as e:
        raise RepoError(
            f"DB connection failed: {e}. "
            "Check .env (EVENTHUB_DATABASE_URL / EVENTHUB_DB_URL), driver installation, and network access."
        )


# =========================
# Row mapping
# =========================
def _row_to_user(row: Any) -> UserInDB:
    # SELECT Id, Username, Email, password_hash, role, is_active
    return UserInDB(
        id=int(row[0]),
        username=row[1],
        email=row[2],
        password_hash=row[3],
        role=(row[4] or "USER").upper(),
        is_active=bool(row[5]),
    )


# =========================
# Interface
# =========================
class UsersRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserInDB]: ...
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserInDB]: ...
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserInDB]: ...
    @abstractmethod
    def create(self, data: UserCreate, password_hash: str, role: str = "USER") -> UserInDB: ...

    def get_or_create_by_email(
        self, email: str, username_hint: str | None = None, role: str = "USER"
    ) -> Tuple[UserInDB, bool]:
        """
        Convenience ל-JWT: מחזיר (user, created_now?).
        אם אין משתמש – יוצר עם password_hash="N/A".
        """
        email_n = _normalize_email(email)
        u = self.get_by_email(email_n)
        if u:
            return u, False
        return self.create(
            UserCreate(
                username=_normalize_username(username_hint or email_n.split("@")[0]),
                email=email_n,
            ),
            password_hash="N/A",
            role=role,
        ), True


# =========================
# SQL (pyodbc) impl
# =========================
class SqlUsersRepository(UsersRepository):
    def get_by_email(self, email: str) -> Optional[UserInDB]:
        email = _normalize_email(email)
        if not email:
            return None
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT Id, Username, Email, password_hash, role, is_active "
                "FROM Users WHERE LOWER(Email) = LOWER(?)",
                (email.lower(),),
            )
            row = cur.fetchone()
        return _row_to_user(row) if row else None

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        username = (username or "").strip()
        if not username:
            return None
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT Id, Username, Email, password_hash, role, is_active "
                "FROM Users WHERE LOWER(Username) = LOWER(?)",
                (username.lower(),),
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
        return __row_to_user(row) if row else None

    def _map_integrity_error(self, e: pyodbc.IntegrityError) -> RepoError:
        """
        Map SQL Server unique violations to domain errors.
        Looks for 2601/2627 and index names in the message (e.g., IX_Users_Username).
        """
        msg = str(e).lower()
        if "2601" in msg or "2627" in msg or "duplicate" in msg:
            if "ix_users_username" in msg or "username" in msg:
                return DuplicateUsernameError("username already exists")
            if "ix_users_email" in msg or "email" in msg:
                return DuplicateEmailError("email already exists")
            return RepoError("duplicate username or email")
        return RepoError(f"integrity error: {e}")

    def create(self, data: UserCreate, password_hash: str, role: str = "USER") -> UserInDB:
        email = _normalize_email(data.email)
        username = _normalize_username(data.username)
        role = _normalize_role(role)

        # Early validations to avoid 500
        if self.get_by_email(email):
            raise DuplicateEmailError("email already exists")
        if self.get_by_username(username):
            raise DuplicateUsernameError("username already exists")

        try:
            with _conn() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO Users (Username, Email, password_hash, role) VALUES (?, ?, ?, ?)",
                    (username, email, password_hash, role),
                )
                cur.execute(
                    "SELECT Id, Username, Email, password_hash, role, is_active "
                    "FROM Users WHERE LOWER(Email) = LOWER(?)",
                    (email.lower(),),
                )
                row = cur.fetchone()
        except pyodbc.IntegrityError as e:
            raise self._map_integrity_error(e) from e
        except pyodbc.Error as e:
            raise RepoError(f"DB error on create user: {e}") from e

        if not row:
            raise RepoError("Insert succeeded but no row returned")

        return _row_to_user(row)


# =========================
# In-Memory fallback
# =========================
class InMemoryUsersRepository(UsersRepository):
    def __init__(self) -> None:
        self._by_id: Dict[int, UserInDB] = {}
        self._by_email: Dict[str, int] = {}
        self._by_username: Dict[str, int] = {}
        self._next_id = 1

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        uid = self._by_email.get(_normalize_email(email))
        return self._by_id.get(uid) if uid else None

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        uid = self._by_username.get((username or "").strip().lower())
        return self._by_id.get(uid) if uid else None

    def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        return self._by_id.get(int(user_id))

    def create(self, data: UserCreate, password_hash: str, role: str = "USER") -> UserInDB:
        email = _normalize_email(data.email)
        username = _normalize_username(data.username)
        role = _normalize_role(role)

        if self.get_by_email(email):
            raise DuplicateEmailError("email already exists")
        if self.get_by_username(username):
            raise DuplicateUsernameError("username already exists")

        uid = self._next_id
        self._next_id += 1
        user = UserInDB(
            id=uid,
            email=email,
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        self._by_id[uid] = user
        self._by_email[email] = uid
        self._by_username[username.lower()] = uid
        return user


# =========================
# Repo selector
# =========================
FORCE_SQL_USERS = os.getenv("FORCE_SQL_USERS", "1") == "1"

def _make_users_repo() -> UsersRepository:
    try:
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT TOP 1 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Users'")
            if not cur.fetchone():
                raise RepoError("Users table not found in DB")
        print("[UsersRepository] Using SQL repository")
        return SqlUsersRepository()
    except Exception as e:
        if FORCE_SQL_USERS:
            # fail loud to avoid hidden fallbacks that break invariants later
            raise RepoError(
                f"[UsersRepository] Failed to init SQL repository: {e}\n"
                f"Hint: Ensure EVENTHUB_DATABASE_URL / EVENTHUB_DB_URL are valid and a SQL Server ODBC driver is installed."
            )
        print(f"[UsersRepository] Falling back to InMemory repository (DB error: {e})")
        return InMemoryUsersRepository()

repo_users: UsersRepository = _make_users_repo()
