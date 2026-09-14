from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentType


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    document_type: DocumentType
    version: int
    content: str
    instructions: str | None
    provider: str
    created_at: datetime


class DocumentGenerateRequest(BaseModel):
    document_type: DocumentType
    instructions: str | None = None


class DocumentImproveRequest(BaseModel):
    instruction: str
