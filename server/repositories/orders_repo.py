from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
from server.models.order import Registration, RegistrationCreate

class OrdersRepository(ABC):
    @abstractmethod
    def create(self, user_id: str, data: RegistrationCreate) -> Registration: ...
    @abstractmethod
    def get(self, reg_id: str) -> Optional[Registration]: ...
    @abstractmethod
    def list_for_user(self, user_id: str) -> List[Registration]: ...

class InMemoryOrdersRepository(OrdersRepository):
    def __init__(self) -> None:
        self._items: dict[str, Registration] = {}
        self._by_user: dict[str, list[str]] = {}

    def create(self, user_id: str, data: RegistrationCreate) -> Registration:
        reg = Registration(
            id=str(uuid4()),
            user_id=user_id,
            event_id=data.event_id,
            notes=data.notes,
            created_at=datetime.utcnow(),
        )
        self._items[reg.id] = reg
        self._by_user.setdefault(user_id, []).append(reg.id)
        return reg

    def get(self, reg_id: str) -> Optional[Registration]:
        return self._items.get(reg_id)

    def list_for_user(self, user_id: str) -> List[Registration]:
        ids = self._by_user.get(user_id, [])
        return [self._items[i] for i in ids]

# default repo instance; later swap to DB-backed impl
repo_orders = InMemoryOrdersRepository()
