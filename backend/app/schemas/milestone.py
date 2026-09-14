from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MilestoneCreate(BaseModel):
    title: str
    start_date: date
    end_date: date | None = None
    notes: str | None = None


class MilestoneUpdate(BaseModel):
    title: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class MilestoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    start_date: date
    end_date: date | None
    notes: str | None
    created_at: datetime
