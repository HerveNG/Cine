from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.document import DocumentType
from app.models.user import User
from app.schemas.document import DocumentGenerateRequest, DocumentImproveRequest, DocumentRead
from app.services.document_service import DocumentService

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["ai-writer"])


@router.get("", response_model=list[DocumentRead])
def list_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService(db).list_documents(project_id, current_user)


@router.get("/{document_type}/versions", response_model=list[DocumentRead])
def list_document_versions(
    project_id: int,
    document_type: DocumentType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService(db).get_history(project_id, document_type, current_user)


@router.post("/generate", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def generate_document(
    project_id: int,
    payload: DocumentGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService(db).generate(
        project_id, payload.document_type, payload.instructions, current_user
    )


@router.post(
    "/{document_id}/regenerate", response_model=DocumentRead, status_code=status.HTTP_201_CREATED
)
def regenerate_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService(db).regenerate(project_id, document_id, current_user)


@router.post(
    "/{document_id}/improve", response_model=DocumentRead, status_code=status.HTTP_201_CREATED
)
def improve_document(
    project_id: int,
    document_id: int,
    payload: DocumentImproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService(db).improve(project_id, document_id, payload.instruction, current_user)


@router.post(
    "/{document_id}/shorten", response_model=DocumentRead, status_code=status.HTTP_201_CREATED
)
def shorten_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DocumentService(db).shorten(project_id, document_id, current_user)
