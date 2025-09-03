# server/repositories/orders_repo.py
from __future__ import annotations
from typing import Optional, List, Dict, Any
from decimal import Decimal
import pyodbc

from server.config import settings
from server.models.order import Registration, RegistrationCreate
from server.repositories.events_repo import repo_events

def _conn():
    return pyodbc.connect(settings.DB_URL)

def _row_to_dict(cur, row) -> Dict[str, Any]:
    cols = [c[0] for c in cur.description]
    return {cols[i]: row[i] for i in range(len(cols))}

def _extract_price(ev: Any) -> float:
    """
    מקבל אובייקט אירוע (Pydantic או dict) ומחזיר מחיר כ-float.
    תומך בשם שדה price/Price ו-NONE/Decimal.
    """
    val = None
    if ev is None:
        val = 0
    elif hasattr(ev, "price"):
        val = getattr(ev, "price")
    elif hasattr(ev, "Price"):
        val = getattr(ev, "Price")
    elif isinstance(ev, dict):
        val = ev.get("price", ev.get("Price"))
    else:
        val = 0

    if val is None:
        return 0.0
    if isinstance(val, Decimal):
        return float(val)
    return float(val)

class OrdersRepositoryDB:
    def create(self, user_id: int, data: RegistrationCreate) -> Registration:
        # 1) מחיר מהאירוע (מתוך ה-Repo של אירועים)
        ev = repo_events.get(data.event_id)
        if not ev:
            raise ValueError("event not found")
        unit_price = _extract_price(ev)
        total = unit_price * int(data.quantity)

        sql = """
        INSERT INTO dbo.Orders (UserId, EventId, Quantity, TotalPrice)
        OUTPUT INSERTED.Id, INSERTED.UserId, INSERTED.EventId,
               INSERTED.Quantity, INSERTED.TotalPrice, INSERTED.CreatedAt
        VALUES (?, ?, ?, ?)
        """
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (int(user_id), int(data.event_id), int(data.quantity), total))
            row = cur.fetchone()
            conn.commit()
            d = _row_to_dict(cur, row)
            return Registration(
                id=d["Id"],
                user_id=d["UserId"],
                event_id=d["EventId"],
                quantity=d["Quantity"],
                total_price=float(d["TotalPrice"]),
                created_at=d["CreatedAt"],
            )

    def get(self, reg_id: int) -> Optional[Registration]:
        sql = """
        SELECT Id, UserId, EventId, Quantity, TotalPrice, CreatedAt
        FROM dbo.Orders WHERE Id = ?
        """
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (int(reg_id),))
            row = cur.fetchone()
            if not row:
                return None
            d = _row_to_dict(cur, row)
            return Registration(
                id=d["Id"],
                user_id=d["UserId"],
                event_id=d["EventId"],
                quantity=d["Quantity"],
                total_price=float(d["TotalPrice"]),
                created_at=d["CreatedAt"],
            )

    def list_for_user(self, user_id: int) -> List[Registration]:
        sql = """
        SELECT Id, UserId, EventId, Quantity, TotalPrice, CreatedAt
        FROM dbo.Orders
        WHERE UserId = ?
        ORDER BY CreatedAt DESC
        """
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (int(user_id),))
            rows = cur.fetchall()
            out: List[Registration] = []
            for r in rows:
                d = _row_to_dict(cur, r)
                out.append(Registration(
                    id=d["Id"],
                    user_id=d["UserId"],
                    event_id=d["EventId"],
                    quantity=d["Quantity"],
                    total_price=float(d["TotalPrice"]),
                    created_at=d["CreatedAt"],
                ))
            return out

    def analytics_for_user(self, user_id: int) -> dict:
        """
        מחזיר סיכום אישי למשתמש:
        - totals: סך הזמנות, סך כרטיסים (Quantity), סך עלות (TotalPrice)
        - byMonth: חלוקה לפי חודש ההזמנה (CreatedAt)
        - byCategory: לפי קטגוריית האירוע שהוזמן (Events.Category)
        """
        # totals
        sql_totals = """
        SELECT 
            COUNT(*)               AS orders_count,
            COALESCE(SUM(Quantity), 0)     AS tickets_sum,
            COALESCE(SUM(TotalPrice), 0.0) AS spent_sum
        FROM dbo.Orders
        WHERE UserId = ?
        """
        # byMonth – לפי מועד ההזמנה (CreatedAt)
        sql_month = """
        SELECT 
            FORMAT(CreatedAt, 'yyyy-MM') AS [Month],
            COUNT(*)                      AS Orders,
            COALESCE(SUM(Quantity), 0)    AS Tickets,
            COALESCE(SUM(TotalPrice), 0)  AS Spent
        FROM dbo.Orders
        WHERE UserId = ?
        GROUP BY FORMAT(CreatedAt, 'yyyy-MM')
        ORDER BY [Month] ASC
        """
        # byCategory – לפי קטגוריית האירוע (Events.Category)
        sql_cat = """
        SELECT 
            COALESCE(e.Category, 'Uncategorized') AS Category,
            COUNT(*)                               AS Orders,
            COALESCE(SUM(o.Quantity), 0)          AS Tickets,
            COALESCE(SUM(o.TotalPrice), 0)        AS Spent
        FROM dbo.Orders o
        JOIN dbo.Events e ON e.Id = o.EventId
        WHERE o.UserId = ?
        GROUP BY e.Category
        ORDER BY Spent DESC, Orders DESC
        """

        with _conn() as conn:
            cur = conn.cursor()

            # totals
            cur.execute(sql_totals, (int(user_id),))
            trow = cur.fetchone()
            totals = {
                "orders_count": int(trow[0] or 0),
                "tickets_sum": int(trow[1] or 0),
                "spent_sum": float(trow[2] or 0.0),
            }

            # byMonth
            cur.execute(sql_month, (int(user_id),))
            cols = [c[0] for c in cur.description]
            by_month = [dict(zip(cols, r)) for r in cur.fetchall()]
            # מיפוי מפתחות לשמות שמודל ה-Pydantic מצפה להם
            by_month = [
                {
                    "month": m["Month"],
                    "orders": int(m["Orders"]),
                    "tickets": int(m["Tickets"]),
                    "spent": float(m["Spent"]),
                }
                for m in by_month
            ]

            # byCategory
            cur.execute(sql_cat, (int(user_id),))
            cols = [c[0] for c in cur.description]
            by_cat = [dict(zip(cols, r)) for r in cur.fetchall()]
            by_cat = [
                {
                    "category": c["Category"] if c["Category"] is not None else "Uncategorized",
                    "orders": int(c["Orders"]),
                    "tickets": int(c["Tickets"]),
                    "spent": float(c["Spent"]),
                }
                for c in by_cat
            ]

        return {"totals": totals, "byMonth": by_month, "byCategory": by_cat}

# אינסטנס לשימוש בראוטר
repo_orders = OrdersRepositoryDB()
