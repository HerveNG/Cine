from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BudgetLineItemCreate(BaseModel):
    label: str
    quantity: Decimal = Decimal("1")
    unit_cost: Decimal
    notes: str | None = None


class BudgetLineItemUpdate(BaseModel):
    label: str | None = None
    quantity: Decimal | None = None
    unit_cost: Decimal | None = None
    notes: str | None = None


class BudgetLineItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    label: str
    quantity: Decimal
    unit_cost: Decimal
    notes: str | None
    subtotal: Decimal
    created_at: datetime


class BudgetCategoryCreate(BaseModel):
    name: str


class BudgetCategoryUpdate(BaseModel):
    name: str | None = None


class BudgetCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    position: int
    line_items: list[BudgetLineItemRead]
    subtotal: Decimal


class BudgetSummary(BaseModel):
    currency: str | None
    categories: list[BudgetCategoryRead]
    total: Decimal
