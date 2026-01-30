from sqlalchemy.orm import Session
from app.models.job import Job

def handle_document_ingest(job:Job,db:Session):
    #place holder for data ingestion logic
    print(f"worker starting job {job.id} for target {job.target_id}")

    #simulate work
    import time
    time.sleep(10)
    print(f"worker completed job {job.id} for target {job.target_id}")

    
