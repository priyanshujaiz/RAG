from sqlalchemy.orm import Session
from app.models.workspace_membership import WorkspaceMembership
from uuid import UUID

class WorkspaceMembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, membership: WorkspaceMembership) -> WorkspaceMembership:
        self.db.add(membership)
        self.db.flush()
        return membership

    def get_membership(self, user_id: UUID, workspace_id: UUID) -> WorkspaceMembership:
        """
        Checks if a specific user is an active member of a specific workspace.
        """
        return (
            self.db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.user_id == user_id,
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.is_active == True
            )
            .first()
        )

    def list_members(self, workspace_id: UUID):
        """
        Returns all active membership records for a specific workspace.
        """
        return (
            self.db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.is_active == True
            )
            .all()
        )