from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.project import ProjectStatus, ProjectType


class ProjectBase(BaseModel):
    title: str
    project_type: ProjectType
    genre: str | None = None
    country: str | None = None
    language: str | None = None
    duration_minutes: int | None = None
    logline: str | None = None
    short_synopsis: str | None = None
    long_synopsis: str | None = None
    theme: str | None = None
    target_audience: str | None = None
    budget_currency: str | None = None


class ProjectCreate(ProjectBase):
    status: ProjectStatus = ProjectStatus.IDEA


class ProjectUpdate(BaseModel):
    title: str | None = None
    project_type: ProjectType | None = None
    genre: str | None = None
    country: str | None = None
    language: str | None = None
    duration_minutes: int | None = None
    logline: str | None = None
    short_synopsis: str | None = None
    long_synopsis: str | None = None
    theme: str | None = None
    target_audience: str | None = None
    budget_currency: str | None = None
    status: ProjectStatus | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
