import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from app.core.database import Base

class AIRun(Base):
    __tablename__="ai_runs"

    id=Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    #Tenant Isoltaion: Every ai action must be scoped to a project.
    project_id=Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False
    )

    #Link to background job that triggered this run.
    job_id=Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id"),
        nullable=True
    )

    run_type=Column(
        String,
        nullable=False
    )

    status=Column(
        String,
        nullable=False,
        default="CREATED"
    )

    #Prompt input
    input_payload=Column(JSON,nullable=True)

    #LLM response 
    output_payload=Column(JSON,nullable=True)

    #Error message if any
    error_message=Column(Text,nullable=True)

    #Timing and performance
    started_at=Column(DateTime(timezone=True),nullable=True)
    finished_at=Column(DateTime(timezone=True),nullable=True)

    created_at=Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    #relationships
    project= relationship("Project", back_populates="ai_runs")
    job=relationship("Job") #One way link to trigger job.
    
