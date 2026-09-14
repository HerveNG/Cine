import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class DocumentType(str, enum.Enum):
    LOGLINE = "LOGLINE"
    SYNOPSIS_SHORT = "SYNOPSIS_SHORT"
    SYNOPSIS_LONG = "SYNOPSIS_LONG"
    NOTE_INTENTION = "NOTE_INTENTION"
    TRAITEMENT = "TRAITEMENT"
    PITCH = "PITCH"


class Document(Base):
    """A generated AI Writer document.

    Versioned by row rather than by a separate table: every generate/
    regenerate/improve/shorten call inserts a new row with `version`
    incremented for that (project_id, document_type) pair. The current
    version is simply the row with the highest `version` for that pair
    — see DocumentRepository.latest_by_type.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    project: Mapped["Project"] = relationship("Project", back_populates="documents")
