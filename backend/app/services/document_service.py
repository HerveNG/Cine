from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentType
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.ai.factory import get_ai_provider
from app.services.ai.prompts import (
    SYSTEM_PROMPT,
    build_generation_prompt,
    build_improve_prompt,
    build_shorten_prompt,
)
from app.services.project_service import ProjectService


class DocumentService:
    """Orchestrates AI Writer document generation and versioning.

    Every entry point starts by resolving the project through
    ProjectService.get_project, which is the single choke point for user
    data isolation (404 — not 403 — for a project the caller doesn't
    own). Documents themselves are never queried by user_id directly.
    """

    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectService(db)
        self.documents = DocumentRepository(db)

    def list_documents(self, project_id: int, current_user: User) -> list[Document]:
        project = self.projects.get_project(project_id, current_user)
        return list(self.documents.latest_by_type(project.id).values())

    def get_history(
        self, project_id: int, document_type: DocumentType, current_user: User
    ) -> list[Document]:
        project = self.projects.get_project(project_id, current_user)
        return self.documents.list_versions(project.id, document_type)

    def _get_document_or_404(self, project_id: int, document_id: int) -> Document:
        document = self.documents.get_by_id(document_id, project_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable.")
        return document

    def _save_new_version(
        self,
        project_id: int,
        document_type: DocumentType,
        content: str,
        instructions: str | None,
        provider_name: str,
    ) -> Document:
        version = self.documents.get_next_version(project_id, document_type)
        document = Document(
            project_id=project_id,
            document_type=document_type,
            version=version,
            content=content,
            instructions=instructions,
            provider=provider_name,
        )
        return self.documents.create(document)

    def generate(
        self,
        project_id: int,
        document_type: DocumentType,
        instructions: str | None,
        current_user: User,
    ) -> Document:
        project = self.projects.get_project(project_id, current_user)
        provider = get_ai_provider()
        prompt = build_generation_prompt(project, document_type, instructions)
        content = provider.generate(SYSTEM_PROMPT, prompt)
        return self._save_new_version(project.id, document_type, content, instructions, provider.name)

    def regenerate(self, project_id: int, document_id: int, current_user: User) -> Document:
        project = self.projects.get_project(project_id, current_user)
        source = self._get_document_or_404(project.id, document_id)
        provider = get_ai_provider()
        prompt = build_generation_prompt(project, source.document_type, source.instructions)
        content = provider.generate(SYSTEM_PROMPT, prompt)
        return self._save_new_version(
            project.id, source.document_type, content, source.instructions, provider.name
        )

    def improve(
        self, project_id: int, document_id: int, instruction: str, current_user: User
    ) -> Document:
        project = self.projects.get_project(project_id, current_user)
        source = self._get_document_or_404(project.id, document_id)
        provider = get_ai_provider()
        prompt = build_improve_prompt(project, source.document_type, source.content, instruction)
        content = provider.generate(SYSTEM_PROMPT, prompt)
        return self._save_new_version(
            project.id, source.document_type, content, instruction, provider.name
        )

    def shorten(self, project_id: int, document_id: int, current_user: User) -> Document:
        project = self.projects.get_project(project_id, current_user)
        source = self._get_document_or_404(project.id, document_id)
        provider = get_ai_provider()
        prompt = build_shorten_prompt(project, source.document_type, source.content)
        content = provider.generate(SYSTEM_PROMPT, prompt)
        return self._save_new_version(
            project.id, source.document_type, content, source.instructions, provider.name
        )
