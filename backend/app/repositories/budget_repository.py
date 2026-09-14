from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import BudgetCategory, BudgetLineItem


class BudgetRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_categories_for_project(self, project_id: int) -> list[BudgetCategory]:
        stmt = (
            select(BudgetCategory)
            .where(BudgetCategory.project_id == project_id)
            .order_by(BudgetCategory.position, BudgetCategory.id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_category(self, category_id: int, project_id: int) -> BudgetCategory | None:
        stmt = select(BudgetCategory).where(
            BudgetCategory.id == category_id, BudgetCategory.project_id == project_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create_category(self, category: BudgetCategory) -> BudgetCategory:
        stmt = select(func.max(BudgetCategory.position)).where(
            BudgetCategory.project_id == category.project_id
        )
        max_position = self.db.execute(stmt).scalar_one_or_none()
        category.position = (max_position or 0) + 1
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update_category(self, category: BudgetCategory) -> BudgetCategory:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category: BudgetCategory) -> None:
        self.db.delete(category)
        self.db.commit()

    def get_line_item(self, item_id: int, category_id: int) -> BudgetLineItem | None:
        stmt = select(BudgetLineItem).where(
            BudgetLineItem.id == item_id, BudgetLineItem.category_id == category_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_line_item_by_id(self, item_id: int) -> BudgetLineItem | None:
        return self.db.get(BudgetLineItem, item_id)

    def create_line_item(self, item: BudgetLineItem) -> BudgetLineItem:
        stmt = select(func.max(BudgetLineItem.position)).where(
            BudgetLineItem.category_id == item.category_id
        )
        max_position = self.db.execute(stmt).scalar_one_or_none()
        item.position = (max_position or 0) + 1
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_line_item(self, item: BudgetLineItem) -> BudgetLineItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_line_item(self, item: BudgetLineItem) -> None:
        self.db.delete(item)
        self.db.commit()
