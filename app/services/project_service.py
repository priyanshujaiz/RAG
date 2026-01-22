from uuid import UUID
from sqlalchemy.orm import Session
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.workspace_membership_repository import WorkspaceMembershipRepository

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        # Initialize all necessary repositories
        self.project_repo = ProjectRepository(db)
        self.workspace_repo = WorkspaceRepository(db)
        self.membership_repo = WorkspaceMembershipRepository(db)

    def create_project(
        self,
        user_id: UUID,
        workspace_id: UUID,
        name: str
    ) -> Project:
        """
        Creates a new project after validating workspace existence 
        and user membership.
        """
        # 1. Validate Workspace Exists
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise ValueError("Workspace does not exist or has been deleted")

        # 2. Validate User Membership (Security Check)
        membership = self.membership_repo.get_membership(
            user_id=user_id,
            workspace_id=workspace_id
        )
        if not membership:
            raise ValueError("User is not a member of this workspace")

        # 3. Create Project Instance
        new_project = Project(
            name=name,
            workspace_id=workspace_id,
            created_by=user_id
        )

        try:
            # 4. Add to Session (Flush)
            project = self.project_repo.create(new_project)
            
            # 5. Commit Transaction (Save to DB)
            self.db.commit()
            
            # 6. Refresh to get ID and server-generated fields
            self.db.refresh(project)
            return project
            
        except Exception as e:
            self.db.rollback()
            raise e

    def list_projects(self, workspace_id: UUID) -> list[Project]:
        """
        Returns all projects for a given workspace.
        """
        # Note: We don't check membership here because the API layer 
        # will handle authorization before calling this.
        return self.project_repo.list_by_workspace(workspace_id)