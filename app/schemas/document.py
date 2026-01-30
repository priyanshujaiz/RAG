from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List

class DocumentResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    created_by: UUID
    created_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

class DocumentVersionResponse(BaseModel):
    id: UUID
    document_id: UUID
    version_number: int
    created_at: datetime
    # We deliberately DO NOT expose file_path or content_hash to the frontend
    # Security by obscurity for internal storage paths

    class Config:
        from_attributes = True