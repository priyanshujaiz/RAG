import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    null
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from app.core.database import Base

class Job(Base):
    __tablename__="jobs"

    id=Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    project_id=Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False
    )

    job_type=Column(String, nullable=False)

    status=Column(String ,nullable=False, default="PENDING")

    target_type=Column(String, nullable=False)
    target_id=Column(UUID(as_uuid=True), nullable=False)

    playload=Column(JSON, nullable=True)

    attempts=Column(Integer, nullable=False, default=0)
    max_attempts=Column(Integer, nullable=False, default=3)

    last_error=Column(Text, nullable=True)

    #timestamp
    created_at=Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    started_at=Column(DateTime(timezone=True), nullable=True)
    completed_at=Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project=relationship("Project", back_populates="jobs")


