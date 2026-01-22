from uuid import UUID
from sqlalchemy.orm import Session
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.workspace_membership_repository import WorkspaceMembershipRepository

class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db
        self.workspace_repo = WorkspaceRepository(db)
        self.membership_repo = WorkspaceMembershipRepository(db)

    def create_workspace(self, user_id: UUID, name: str) -> Workspace:
        """
        Orchestrates the creation of a workspace and automatically
        assigns the creator as the OWNER.
        """
        try:
            new_workspace = Workspace(
                name=name,
                created_by=user_id
            )

            # 2. Persist workspace to DB via repository
            workspace = self.workspace_repo.create(new_workspace)

            # 3. Initialize the Membership object (Business Rule: Creator = OWNER)
            new_membership = WorkspaceMembership(
                user_id=user_id,
                workspace_id=workspace.id,
                role="OWNER",
                is_active=True
            )

            # 4. Persist membership to DB
            self.membership_repo.create(new_membership)
            self.db.commit()
            self.db.refresh(workspace)

            return workspace
        except Exception as e:
            self.db.rollback()
            raise e
        

    def get_user_workspaces(self, user_id: UUID):
        """
        Retrieves all workspaces a user has access to.
        """
        return self.workspace_repo.list_by_user(user_id)

    def get_workspace_details(self, workspace_id: UUID):
        """
        Fetches a single workspace by ID.
        """
        return self.workspace_repo.get_by_id(workspace_id)