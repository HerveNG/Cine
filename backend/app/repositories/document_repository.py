from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentType


class DocumentRepository:
    """Scoped by project_id only — the caller (DocumentService) is
    responsible for verifying the requesting user owns that project
    before calling into this repository, via ProjectService.get_project.
    """

    def __init__(self, db: Session):
        self.db = db

    def latest_by_type(self, project_id: int) -> dict[DocumentType, Document]:
        documents = self.list_all(project_id)
        latest: dict[DocumentType, Document] = {}
        for document in documents:
            current = latest.get(document.document_type)
            if current is None or document.version > current.version:
                latest[document.document_type] = document
        return latest

    def list_all(self, project_id: int) -> list[Document]:
        stmt = select(Document).where(Document.project_id == project_id)
        return list(self.db.execute(stmt).scalars().all())

    def list_versions(self, project_id: int, document_type: DocumentType) -> list[Document]:
        stmt = (
            select(Document)
            .where(Document.project_id == project_id, Document.document_type == document_type)
            .order_by(Document.version.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, document_id: int, project_id: int) -> Document | None:
        stmt = select(Document).where(
            Document.id == document_id, Document.project_id == project_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_next_version(self, project_id: int, document_type: DocumentType) -> int:
        stmt = select(func.max(Document.version)).where(
            Document.project_id == project_id, Document.document_type == document_type
        )
        current_max = self.db.execute(stmt).scalar_one_or_none()
        return (current_max or 0) + 1

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def count_for_projects(self, project_ids: list[int]) -> int:
        if not project_ids:
            return 0
        stmt = select(func.count()).select_from(Document).where(
            Document.project_id.in_(project_ids)
        )
        return self.db.execute(stmt).scalar_one()
