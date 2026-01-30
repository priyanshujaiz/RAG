import time 
import sys
import os

sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.repositories.job_repository import JobRepository
from app.workers.dispatcher import dispatch_job

POLL_INTERVAL=2

def run_worker():
    print("Worker started")

    while True:

        db:Session=SessionLocal()

        try:
            job_repo=JobRepository(db)

            jobs=job_repo.get_next_pending(limit=1)

            if not jobs:
                time.sleep(POLL_INTERVAL)
                continue

            job= jobs[0]
            print(f"Processing job {job.id} for target {job.job_type}")

            #Mark job as running
            job_repo.mark_running(job)

            #Dispatch job
            try:
                dispatch_job(job,db)

                #Mark success
                job_repo.mark_success(job)
                print(f"Job {job.id} completed successfully")
            except Exception as e:
                print(f"Job {job.id} failed: {e}")
                job_repo.mark_failed(job,str(e))
        except Exception as e:
            print(f"Error processing job: {e}")
            time.sleep(POLL_INTERVAL)
        finally:
            db.close()
            print("Worker shutting down")

if __name__=="__main__":
    run_worker()