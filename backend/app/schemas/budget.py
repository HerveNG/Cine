from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BudgetLineItemCreate(BaseModel):
    label: str = Field(min_length=1)
    quantity: Decimal = Field(default=Decimal("1"), ge=0)
    unit_cost: Decimal = Field(ge=0)
    notes: str | None = None


class BudgetLineItemUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1)
    quantity: Decimal | None = Field(default=None, ge=0)
    unit_cost: Decimal | None = Field(default=None, ge=0)
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
    name: str = Field(min_length=1)


class BudgetCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)


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
