from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_membership_repository import WorkspaceMembershipRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.models.user import User
from uuid import UUID
from app.repositories.project_repository import ProjectRepository
from app.models.project import Project

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = UserRepository().get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def get_current_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifies that the user belongs to the workspace and the workspace exists.
    Returns (workspace, membership) tuple.
    """
    membership_repo = WorkspaceMembershipRepository(db)
    workspace_repo = WorkspaceRepository(db)

    membership = membership_repo.get_membership(
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    workspace = workspace_repo.get_by_id(workspace_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    return workspace, membership

def require_workspace_role(allowed_roles: list[str]):
    """
    Factory dependency to enforce specific roles.
    Usage: Depends(require_workspace_role(["OWNER", "ADMIN"]))
    """
    def _role_checker(
        workspace_and_membership = Depends(get_current_workspace)
    ):
        _, membership = workspace_and_membership

        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return membership

    return _role_checker
    

def get_current_project(
    project_id: UUID,
    workspace_and_membership = Depends(get_current_workspace),
    db: Session = Depends(get_db)
) -> Project:
    """
    Validates that the project exists AND belongs to the current workspace.
    """
    # 1. Reuse existing security context (User + Workspace)
    # This automatically enforces: User is logged in AND is a member of this workspace
    workspace, _ = workspace_and_membership

    # 2. Fetch Project
    project_repo = ProjectRepository(db)
    project = project_repo.get_by_id(project_id)

    # 3. Validation Chain
    # Check A: Does it exist?
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check B: Does it belong to this workspace? 
    if project.workspace_id != workspace.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project