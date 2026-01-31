import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Enforces tenant boundary: A project MUST belong to a workspace
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False
    )

    name = Column(String, nullable=False)

    # Audit field: Who started this project?
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
    workspace = relationship("Workspace", back_populates="projects")
    # later we will add: documents, chats, etc.
    documents = relationship("Document", back_populates="project")

    jobs=relationship("Job", back_populates="project")
    ai_runs=relationship("AIRun", back_populates="project")