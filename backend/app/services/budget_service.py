from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.budget import BudgetCategory, BudgetLineItem
from app.models.user import User
from app.repositories.budget_repository import BudgetRepository
from app.schemas.budget import (
    BudgetCategoryCreate,
    BudgetCategoryRead,
    BudgetCategoryUpdate,
    BudgetLineItemCreate,
    BudgetLineItemRead,
    BudgetLineItemUpdate,
    BudgetSummary,
)
from app.services.project_service import ProjectService


TWO_PLACES = Decimal("0.01")


def _item_to_read(item: BudgetLineItem) -> BudgetLineItemRead:
    return BudgetLineItemRead(
        id=item.id,
        category_id=item.category_id,
        label=item.label,
        quantity=item.quantity,
        unit_cost=item.unit_cost,
        notes=item.notes,
        subtotal=(item.quantity * item.unit_cost).quantize(TWO_PLACES),
        created_at=item.created_at,
    )


def _category_to_read(category: BudgetCategory) -> BudgetCategoryRead:
    items = [_item_to_read(i) for i in category.line_items]
    return BudgetCategoryRead(
        id=category.id,
        project_id=category.project_id,
        name=category.name,
        position=category.position,
        line_items=items,
        subtotal=sum((i.subtotal for i in items), Decimal("0")),
    )


class BudgetService:
    """Every entry point resolves the project via ProjectService.get_project
    first (404 for a project the caller doesn't own), matching the
    isolation pattern used by DocumentService and FundingService. Subtotals
    are always computed here from quantity/unit_cost — never stored — so
    there's a single source of truth for every amount.
    """

    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectService(db)
        self.budget = BudgetRepository(db)

    def get_summary(self, project_id: int, current_user: User) -> BudgetSummary:
        project = self.projects.get_project(project_id, current_user)
        categories = [
            _category_to_read(c) for c in self.budget.list_categories_for_project(project.id)
        ]
        return BudgetSummary(
            currency=project.budget_currency,
            categories=categories,
            total=sum((c.subtotal for c in categories), Decimal("0")),
        )

    def create_category(
        self, project_id: int, payload: BudgetCategoryCreate, current_user: User
    ) -> BudgetCategoryRead:
        project = self.projects.get_project(project_id, current_user)
        category = BudgetCategory(project_id=project.id, name=payload.name)
        category = self.budget.create_category(category)
        return _category_to_read(category)

    def _get_category_or_404(self, project_id: int, category_id: int) -> BudgetCategory:
        category = self.budget.get_category(category_id, project_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable.")
        return category

    def update_category(
        self, project_id: int, category_id: int, payload: BudgetCategoryUpdate, current_user: User
    ) -> BudgetCategoryRead:
        project = self.projects.get_project(project_id, current_user)
        category = self._get_category_or_404(project.id, category_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        category = self.budget.update_category(category)
        return _category_to_read(category)

    def delete_category(self, project_id: int, category_id: int, current_user: User) -> None:
        project = self.projects.get_project(project_id, current_user)
        category = self._get_category_or_404(project.id, category_id)
        self.budget.delete_category(category)

    def create_line_item(
        self, project_id: int, category_id: int, payload: BudgetLineItemCreate, current_user: User
    ) -> BudgetLineItemRead:
        project = self.projects.get_project(project_id, current_user)
        self._get_category_or_404(project.id, category_id)
        item = BudgetLineItem(category_id=category_id, **payload.model_dump())
        item = self.budget.create_line_item(item)
        return _item_to_read(item)

    def _get_item_or_404(self, project_id: int, item_id: int) -> BudgetLineItem:
        item = self.budget.get_line_item_by_id(item_id)
        if item is None or self.budget.get_category(item.category_id, project_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ligne introuvable.")
        return item

    def update_line_item(
        self, project_id: int, item_id: int, payload: BudgetLineItemUpdate, current_user: User
    ) -> BudgetLineItemRead:
        project = self.projects.get_project(project_id, current_user)
        item = self._get_item_or_404(project.id, item_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        item = self.budget.update_line_item(item)
        return _item_to_read(item)

    def delete_line_item(self, project_id: int, item_id: int, current_user: User) -> None:
        project = self.projects.get_project(project_id, current_user)
        item = self._get_item_or_404(project.id, item_id)
        self.budget.delete_line_item(item)
