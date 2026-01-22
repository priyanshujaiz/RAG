from sqlalchemy.orm import Session
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership
from uuid import UUID

class WorkspaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, workspace: Workspace) -> Workspace:
        self.db.add(workspace)
        self.db.flush()
        return workspace

    def get_by_id(self, workspace_id: UUID) -> Workspace:
        return (
            self.db.query(Workspace)
            .filter(
                Workspace.id == workspace_id,
                Workspace.is_deleted == False
            )
            .first()
        )

    def list_by_user(self, user_id: UUID):
        return (
            self.db.query(Workspace)
            .join(WorkspaceMembership)
            .filter(
                WorkspaceMembership.user_id == user_id,
                WorkspaceMembership.is_active == True,
                Workspace.is_deleted == False
            )
            .all()
        )