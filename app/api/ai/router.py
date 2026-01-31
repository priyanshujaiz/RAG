from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_project
from app.services.ai_execution_services import AIExecutionService
from app.repositories.ai_run_repository import AIRunRepository
from app.schemas.ai import AIRunCreate, AIRunResponse
from app.models.user import User

router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects/{project_id}/ai",
    tags=["ai"]
)

#Trigger ai run
@router.post("/runs", response_model=AIRunResponse, status_code=status.HTTP_201_CREATED)
def create_ai_run(
    workspace_id: UUID,
    project_id: UUID,
    data: AIRunCreate,
    project=Depends(get_current_project),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Triggers a new AI run for a given project.
    """
    service = AIExecutionService(db)
    try:
        ai_run=service.create_ai_run(
            project_id=project.id,
            run_type=data.run_type,
            document_ids=data.document_ids,
            parameters=data.parameters
        )

        return ai_run
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

#List ai runs
@router.get("/runs", response_model=List[AIRunResponse])
def list_ai_runs(
    workspace_id: UUID,
    project_id: UUID,
    project=Depends(get_current_project),
    db: Session = Depends(get_db)
):
    """
    Lists all AI runs for a given project.
    """
    repo=AIRunRepository(db)
    return repo.list_by_project(project.id)

#Get run detials
@router.get("/runs/{run_id}", response_model=AIRunResponse)
def get_ai_run(
    workspace_id: UUID,
    project_id: UUID,
    run_id: UUID,
    project=Depends(get_current_project),
    db: Session = Depends(get_db)
):
    """
    Gets the details of a specific AI run.
    """
    repo=AIRunRepository(db)
    ai_run=repo.get_by_id(run_id)

    if not ai_run:
        raise HTTPException(status_code=404, detail="AI run not found")

    if ai_run.project_id != project.id:
        raise HTTPException(status_code=404, detail="AI run not found")
    
    return ai_run