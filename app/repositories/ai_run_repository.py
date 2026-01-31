from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.ai_run import AIRun

class AIRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, run: AIRun) -> AIRun:
        """
        Adds an AI run to the session but allows the Service to commit.
        """
        self.db.add(run)
        self.db.flush()
        return run

    def get_by_id(self, run_id: UUID) -> AIRun | None:

        return (
            self.db.query(AIRun)
            .filter(AIRun.id == run_id)
            .first()
        )
    
    def list_by_project(self, project_id: UUID) -> list[AIRun]:
        return (
            self.db.query(AIRun)
            .filter(AIRun.project_id == project_id)
            .order_by(AIRun.created_at.desc())
            .all()
        )
    
    def mark_running(self, run: AIRun) -> AIRun:
    
        run.status="RUNNING"
        run.started_at=func.now()
        self.db.commit()
        self.db.refresh(run)
        return run
    
    def mark_success(self, run: AIRun) -> AIRun:
        run.status="SUCCESS"
        run.finished_at=func.now()
        self.db.commit()
        self.db.refresh(run)
        return run
    
    def mark_failed(self, run: AIRun, error: Exception) -> AIRun:
        run.status="FAILED"
        run.finished_at=func.now()
        run.error_message=str(error)
        self.db.commit()
        self.db.refresh(run)
        return run