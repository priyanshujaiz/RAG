from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_workspace
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.models.user import User

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

# 1. CREATE WORKSPACE
@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new workspace and assigns the creator as OWNER.
    """
    service = WorkspaceService(db)
    return service.create_workspace(
        user_id=current_user.id,
        name=data.name
    )

# 2. LIST USER WORKSPACES
@router.get("", response_model=List[WorkspaceResponse])
def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all workspaces the current user belongs to.
    """
    service = WorkspaceService(db)
    return service.get_user_workspaces(user_id=current_user.id)

# 3. GET WORKSPACE DETAILS (Protected by Dependency)
@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    # This dependency AUTOMATICALLY checks if user is a member
    # If not, it throws 403 Forbidden before this function even runs.
    workspace_and_membership = Depends(get_current_workspace)
):
    """
    Get details of a specific workspace. 
    Only accessible by members.
    """
    workspace, _ = workspace_and_membership
    return workspace