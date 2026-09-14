from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.budget import (
    BudgetCategoryCreate,
    BudgetCategoryRead,
    BudgetCategoryUpdate,
    BudgetLineItemCreate,
    BudgetLineItemRead,
    BudgetLineItemUpdate,
    BudgetSummary,
)
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/projects/{project_id}/budget", tags=["budget"])


@router.get("", response_model=BudgetSummary)
def get_budget_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BudgetService(db).get_summary(project_id, current_user)


@router.post("/categories", response_model=BudgetCategoryRead, status_code=status.HTTP_201_CREATED)
def create_budget_category(
    project_id: int,
    payload: BudgetCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BudgetService(db).create_category(project_id, payload, current_user)


@router.put("/categories/{category_id}", response_model=BudgetCategoryRead)
def update_budget_category(
    project_id: int,
    category_id: int,
    payload: BudgetCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BudgetService(db).update_category(project_id, category_id, payload, current_user)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget_category(
    project_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    BudgetService(db).delete_category(project_id, category_id, current_user)


@router.post(
    "/categories/{category_id}/items",
    response_model=BudgetLineItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_budget_line_item(
    project_id: int,
    category_id: int,
    payload: BudgetLineItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BudgetService(db).create_line_item(project_id, category_id, payload, current_user)


@router.put("/items/{item_id}", response_model=BudgetLineItemRead)
def update_budget_line_item(
    project_id: int,
    item_id: int,
    payload: BudgetLineItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BudgetService(db).update_line_item(project_id, item_id, payload, current_user)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget_line_item(
    project_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    BudgetService(db).delete_line_item(project_id, item_id, current_user)
