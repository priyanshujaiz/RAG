from uuid import UUID
from sqlalchemy.orm import Session
from app.models.project import Project

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project: Project) -> Project:
        """
        Creates a new project in the database.
        """
        self.db.add(project)
        self.db.flush()
        return project

    def get_by_id(self, project_id: UUID) -> Project | None:
        """
        Retrieves a project by ID if it exists and is not deleted.
        """
        return (
            self.db.query(Project)
            .filter(
                Project.id == project_id,
                Project.is_deleted == False
            )
            .first()
        )

    def list_by_workspace(self, workspace_id: UUID) -> list[Project]:
        """
        Lists all active projects belonging to a specific workspace.
        """
        return (
            self.db.query(Project)
            .filter(
                Project.workspace_id == workspace_id,
                Project.is_deleted == False
            )
            .all()
        )