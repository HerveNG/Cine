from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.funding_follow import FundingFollow


class FundingFollowRepository:
    def __init__(self, db: Session):
        self.db = db

    def followed_ids_for_user(self, user_id: int) -> set[int]:
        stmt = select(FundingFollow.opportunity_id).where(FundingFollow.user_id == user_id)
        return set(self.db.execute(stmt).scalars().all())

    def is_following(self, user_id: int, opportunity_id: int) -> bool:
        stmt = select(FundingFollow).where(
            FundingFollow.user_id == user_id, FundingFollow.opportunity_id == opportunity_id
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def follow(self, user_id: int, opportunity_id: int) -> None:
        if self.is_following(user_id, opportunity_id):
            return
        self.db.add(FundingFollow(user_id=user_id, opportunity_id=opportunity_id))
        self.db.commit()

    def unfollow(self, user_id: int, opportunity_id: int) -> None:
        stmt = select(FundingFollow).where(
            FundingFollow.user_id == user_id, FundingFollow.opportunity_id == opportunity_id
        )
        follow = self.db.execute(stmt).scalar_one_or_none()
        if follow is not None:
            self.db.delete(follow)
            self.db.commit()

    def follower_user_ids(self, opportunity_id: int) -> list[int]:
        stmt = select(FundingFollow.user_id).where(FundingFollow.opportunity_id == opportunity_id)
        return list(self.db.execute(stmt).scalars().all())
