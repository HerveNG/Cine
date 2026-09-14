from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MilestoneCreate(BaseModel):
    title: str = Field(min_length=1)
    start_date: date
    end_date: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _end_not_before_start(self) -> "MilestoneCreate":
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("La date de fin ne peut pas précéder la date de début.")
        return self


class MilestoneUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _end_not_before_start(self) -> "MilestoneUpdate":
        if self.start_date is not None and self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("La date de fin ne peut pas précéder la date de début.")
        return self


class MilestoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    start_date: date
    end_date: date | None
    notes: str | None
    created_at: datetime
