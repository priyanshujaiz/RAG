from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_project
from app.services.document_service import DocumentService
from app.storage.local import LocalDiskStorage
from app.schemas.document import DocumentResponse, DocumentVersionResponse
from app.models.user import User

# Path Structure: /workspaces/{id}/projects/{id}/documents
router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects/{project_id}/documents",
    tags=["documents"]
)

# 1. UPLOAD DOCUMENT
@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    workspace_id: UUID,
    project_id: UUID,
    file: UploadFile = File(...),
    project = Depends(get_current_project), # Security: Ensures project exists & user has access
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a text file, creates a document, creates v1, and chunks it.
    """
    # 1. Read File Content (Memory-based for now)
    try:
        content_bytes = file.file.read()
        content_text = content_bytes.decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")

    # 2. Save to Disk (Physical Storage)
    # Strategy: storage_data/{project_id}/{filename}
    storage = LocalDiskStorage()
    file_path = f"documents/{project.id}/{file.filename}"
    storage.save(file_path, content_bytes)

    # 3. Save to DB (Logical Storage)
    service = DocumentService(db)
    document = service.create_document(
        project_id=project.id,
        title=file.filename,
        created_by=current_user.id,
        file_path=file_path,
        content=content_text
    )

    return document

# 2. LIST DOCUMENTS
@router.get("", response_model=List[DocumentResponse])
def list_documents(
    workspace_id: UUID,
    project_id: UUID,
    project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    service = DocumentService(db)
    return service.list_project_documents(project.id)

# 3. GET DOCUMENT DETAILS
@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    workspace_id: UUID,
    project_id: UUID,
    document_id: UUID,
    project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    service = DocumentService(db)
    document = service.get_document_details(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Security Check: Ensure document belongs to the requested project
    if document.project_id != project.id:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return document

# 4. LIST DOCUMENT VERSIONS
@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
def list_versions(
    workspace_id: UUID,
    project_id: UUID,
    document_id: UUID,
    project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    service = DocumentService(db)
    # Optional: Verify document exists and belongs to project first
    document = service.get_document_details(document_id)
    if not document or document.project_id != project.id:
        raise HTTPException(status_code=404, detail="Document not found")

    return service.list_versions(document_id)