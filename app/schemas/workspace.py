from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# Input Schema (What user sends)
class WorkspaceCreate(BaseModel):
    name: str

# Output Schema (What user sees)
class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models