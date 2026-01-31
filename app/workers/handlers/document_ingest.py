from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.repositories.document_version_repository import DocumentVersionRepository
from app.storage.local import LocalDiskStorage

CHUNK_SIZE=500

def handle_document_ingest(job:Job,db:Session):
    #place holder for data ingestion logic
    print(f"worker starting job {job.id} for target {job.target_id}")

    #initialize dependencies
    version_repo=DocumentVersionRepository(db)
    chunk_repo=DocumentChunkRepository(db)
    storage=LocalDiskStorage()

    version=version_repo.get_by_id(job.target_id)
    if not version:
        raise ValueError(f"Document version not found: {job.target_id}")
    
    #Idempotency check to ensure chunks are not re-hashed.
    if chunk_repo.hash_chunks(version.id):
        print(f"worker skipped job {job.id} for target {job.target_id} because chunks are already hashed")
        return

    try:
        content_bytes=storage.read(version.file_path)
        content_text=content_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to read file: {e}")
    
    chunks=[]
    for i,start in enumerate(range(0, len(content_text), CHUNK_SIZE)):
        text_segment=content_text[start:start+CHUNK_SIZE]
        chunks.append(
            DocumentChunk(
                document_version_id=version.id,
                chunk_index=i,
                text=text_segment
            )
        )
    chunk_repo.bulk_create(chunks)

    print(f"worker completed job {job.id} for target {job.target_id}")