import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False
    )
    
    # Structural Versioning (1, 2, 3...)
    version_number = Column(Integer, nullable=False)
    
    # Storage Abstraction (S3 path or local path)
    file_path = Column(String, nullable=False)
    
    # Integrity Check (SHA256 usually)
    content_hash = Column(String, nullable=False)
    
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    document = relationship("Document", back_populates="versions")
    
    # One Version has Many Chunks
    chunks = relationship("DocumentChunk", back_populates="document_version")