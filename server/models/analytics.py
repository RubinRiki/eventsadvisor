# server/models/analytics.py
from pydantic import BaseModel
from typing import List

class OrdersAnalyticsTotals(BaseModel):
    orders_count: int
    tickets_sum: int
    spent_sum: float

class OrdersAnalyticsByMonthItem(BaseModel):
    month: str   # 'YYYY-MM'
    orders: int
    tickets: int
    spent: float

class OrdersAnalyticsByCategoryItem(BaseModel):
    category: str
    orders: int
    tickets: int
    spent: float

class OrdersAnalyticsSummary(BaseModel):
    totals: OrdersAnalyticsTotals
    byMonth: List[OrdersAnalyticsByMonthItem]
    byCategory: List[OrdersAnalyticsByCategoryItem]
