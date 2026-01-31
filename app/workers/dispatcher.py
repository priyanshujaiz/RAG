from sqlalchemy.orm import Session
from app.models.job import Job
from app.workers.handlers.document_ingest import handle_document_ingest
from app.workers.handlers.ai_run import handle_ai_run

def dispatch_job(job:Job,db:Session):
    if job.job_type=="DOCUMENT_INGEST":
        handle_document_ingest(job,db)
    elif job.job_type == "AI_RUN":
        handle_ai_run(job, db)
    else:
        raise ValueError(f"Unknown job type: {job.job_type}")
