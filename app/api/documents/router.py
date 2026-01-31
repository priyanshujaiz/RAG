from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
import hashlib
from app.models.job import Job
from app.repositories.job_repository import JobRepository

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
@router.post("", status_code=status.HTTP_201_CREATED)
def upload_document(
    workspace_id: UUID,
    project_id: UUID,
    file: UploadFile = File(...),
    project = Depends(get_current_project), # Security: Ensures project exists & user has access
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Async Upload document and save file ,create metadata and create version.
    """
    try:
        content_bytes=file.file.read()
        content_hash=hashlib.sha256(content_bytes).hexdigest()

        storage=LocalDiskStorage()
        file_path=f"documents/{project.id}/{file.filename}"
        storage.save(file_path, content_bytes)

        service=DocumentService(db)
        document, version=service.create_document_metadata(
            project_id=project.id,
            title=file.filename,
            created_by=current_user.id,
            file_path=file_path,
            content_hash=content_hash
        )

        job_repo=JobRepository(db)
        new_job=Job(
            project_id=project.id,
            job_type="DOCUMENT_INGEST",
            target_type="DOCUMENT_VERSION",
            target_id=version.id,
            payload={
                "file_name": file.filename,
                "file_path": file_path
            }
        )
        job_repo.create(new_job)

        db.commit()
        return {
            "document_id": document.id,
            "version_id": version.id,
            "job_id": new_job.id,
            "status": "PROCESSING"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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