from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.repositories.funding_follow_repository import FundingFollowRepository
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationRepository(db)
        self.follows = FundingFollowRepository(db)

    def list_for_user(self, current_user: User) -> list[Notification]:
        return self.notifications.list_for_user(current_user.id)

    def mark_read(self, notification_id: int, current_user: User) -> Notification:
        notification = self.notifications.get(notification_id, current_user.id)
        if notification is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification introuvable.")
        return self.notifications.mark_read(notification)

    def mark_all_read(self, current_user: User) -> None:
        self.notifications.mark_all_read(current_user.id)

    def notify_followers(
        self, opportunity_id: int, title: str, body: str, url: str | None
    ) -> int:
        """Fan out a notification to every user following this
        opportunity. Returns the number of notifications created."""
        follower_ids = self.follows.follower_user_ids(opportunity_id)
        for user_id in follower_ids:
            self.notifications.create(
                Notification(user_id=user_id, title=title, body=body, url=url)
            )
        return len(follower_ids)
