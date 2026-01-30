import uuid
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Chunks are tied to a specific VERSION, not the generic document
    document_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_versions.id"),
        nullable=False
    )
    
    # Order matters for context reconstruction
    chunk_index = Column(Integer, nullable=False)
    
    text = Column(Text, nullable=False)
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    document_version = relationship("DocumentVersion", back_populates="chunks")