from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get(self, notification_id: int, user_id: int) -> Notification | None:
        stmt = select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_read(self, user_id: int) -> None:
        stmt = select(Notification).where(
            Notification.user_id == user_id, Notification.is_read.is_(False)
        )
        for notification in self.db.execute(stmt).scalars().all():
            notification.is_read = True
        self.db.commit()
