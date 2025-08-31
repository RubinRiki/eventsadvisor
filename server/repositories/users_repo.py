from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict
from uuid import uuid4
from server.models.user import User, UserCreate

class UsersRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]: ...
    @abstractmethod
    def create(self, data: UserCreate, hashed_password: str, role: str = "user") -> User: ...

class InMemoryUsersRepository(UsersRepository):
    def __init__(self) -> None:
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, str] = {}

    def get_by_email(self, email: str) -> Optional[User]:
        uid = self._by_email.get(email.lower())
        return self._by_id.get(uid) if uid else None

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._by_id.get(user_id)

    def create(self, data: UserCreate, hashed_password: str, role: str = "user") -> User:
        if self.get_by_email(data.email):
            raise ValueError("email already exists")
        uid = str(uuid4())
        user = User(id=uid, email=data.email.lower(), hashed_password=hashed_password, role=role, is_active=True)
        self._by_id[uid] = user
        self._by_email[user.email] = uid
        return user

# default repo instance for now; later you can swap to DB-backed impl
repo_users = InMemoryUsersRepository()
