import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Boolean, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship

class WorkspaceMembership(Base):
    __tablename__ = "workspace_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False
    )

    role = Column(
        Enum("OWNER", "ADMIN", "MEMBER", "VIEWER", name="workspace_role"),
        nullable=False
    )

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    is_active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("user_id", "workspace_id"),
    )

    user = relationship("User", back_populates="workspace_memberships")
    workspace = relationship("Workspace", back_populates="memberships")
