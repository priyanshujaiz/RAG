from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.job import Job

class JobRepository:
    def __init__(self,db:Session):
        self.db=db
    
    def create(self,job:Job)->Job:
        self.db.add(job)
        self.db.flush()
        return job
    
    def get_by_id(self,job_id:UUID)->Job | None:
        return (
            self.db.query(Job)
            .filter(Job.id==job_id)
            .first()
        )

    def get_next_pending(self,limit:int =10)->list[Job]:
        return (
            self.db.query(Job)
            .filter(Job.status=="PENDING")
            .order_by(Job.created_at.asc())
            .limit(limit)
            .all()
        )
    
    def mark_running(self,job:Job)->Job:
        job.status="RUNNING"
        job.started_at=func.now()
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_success(self,job:Job)->Job:
        job.status="SUCCESS"
        job.completed_at=func.now()
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def mark_failed(self,job:Job,error:Exception)->Job:
        job.attempts+=1
        job.last_error=str(error)
        if job.attempts>=job.max_attempts:
            job.status="FAILED"
            job.completed_at=func.now()
        else:
            job.status="PENDING"
        self.db.commit()
        self.db.refresh(job)
        return job

