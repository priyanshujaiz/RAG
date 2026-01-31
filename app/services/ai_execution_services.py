from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.document_repository import DocumentRepository
from app.repositories.document_version_repository import DocumentVersionRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.ai_run_repository import AIRunRepository
from app.repositories.job_repository import JobRepository
from app.models.ai_run import AIRun
from app.models.job import Job

class AIExecutionService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_run_repo = AIRunRepository(db)
        self.job_repo = JobRepository(db)
        self.doc_repo = DocumentRepository(db)
        self.version_repo = DocumentVersionRepository(db)
        self.chunk_repo = DocumentChunkRepository(db)

    def create_ai_run(
        self,
        project_id: UUID,
        run_type: str,
        document_ids: list[UUID],
        parameters: dict
    ) -> AIRun:
        """
        Creates a new AI run for a given project, document IDs, and parameters.
        """
        try:
            documents_payload=[]

            for doc_id in document_ids:
                #check doc belong to project
                document=self.doc_repo.get_by_id(doc_id)
                if not document or document.project_id != project_id:
                    raise ValueError(f"Document {doc_id} not found or does not belong to project {project_id}")
                
                #get latest version
                version=self.version_repo.get_latest(doc_id)
                if not version:
                    continue

                #fetch chunks
                chunks=self.chunk_repo.list_by_version(version.id)

                #Serialize from JSON storage
                documents_payload.append({
                    "document_id": str(doc_id),
                    "document_title": document.title,
                    "version_id": str(version.id),
                    "chunks": [
                        {
                            "chunk_id":str(c.id),
                            "text":c.text,
                            "index":c.chunk_index
                        }
                        for c in chunks
                    ]
                })

            #Construct input payload
            input_payload={
                "run_type":run_type,
                "context_documents":documents_payload,
                "user_parameters":parameters
            }

            #Create AI Run
            ai_run=AIRun(
                project_id=project_id,
                run_type=run_type,
                input_payload=input_payload,
                status="CREATED"
            )
            ai_run=self.ai_run_repo.create(ai_run)
            
            #Queue the execution job 
            job=Job(
                project_id=project_id,
                job_type="AI_RUN",
                target_type="AI_RUN",
                target_id=ai_run.id,
                payload={
                    "run_id":str(ai_run.id),
                }
            )
            self.job_repo.create(job)

            #commit atomically
            self.db.commit()
            self.db.refresh(ai_run)

            return ai_run
        except Exception as e:
            self.db.rollback()
            raise e
        
