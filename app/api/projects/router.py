from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user, 
    get_current_workspace, 
    get_current_project
)
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectResponse
from app.models.user import User


router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects", 
    tags=["projects"]
)

# 1. CREATE PROJECT
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    workspace_id: str, # Required for the URL path to match, even if dependency handles logic
    data: ProjectCreate,
    workspace_and_membership = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new project in the specified workspace.
    """
    workspace, _ = workspace_and_membership
    service = ProjectService(db)
    
    return service.create_project(
        user_id=current_user.id,
        workspace_id=workspace.id,
        name=data.name
    )

# 2. LIST PROJECTS
@router.get("", response_model=List[ProjectResponse])
def list_projects(
    workspace_id: str,
    workspace_and_membership = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """
    Lists all projects in the workspace.
    """
    workspace, _ = workspace_and_membership
    service = ProjectService(db)
    
    return service.list_projects(workspace.id)

# 3. GET PROJECT DETAILS
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    workspace_id: str,
    project_id: str,
    # This dependency AUTOMATICALLY verifies:
    # 1. User is in workspace
    # 2. Project is in workspace
    # 3. Project exists
    project = Depends(get_current_project)
):
    """
    Get a specific project.
    """
    return project