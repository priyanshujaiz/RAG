import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # AI Boundary: Documents are strictly scoped to a Project
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False
    )
    
    title = Column(String, nullable=False)
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    is_deleted = Column(Boolean, default=False)

    # Relationships
    # Using string "Project" avoids circular import issues
    project = relationship("Project", back_populates="documents")
    
    # One Document has Many Versions
    versions = relationship("DocumentVersion", back_populates="document")