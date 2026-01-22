from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# INPUT
class ProjectCreate(BaseModel):
    name: str

# OUTPUT
class ProjectResponse(BaseModel):
    id: UUID
    name: str
    workspace_id: UUID
    created_by: UUID
    created_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models

