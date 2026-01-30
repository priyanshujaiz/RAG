from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk

class DocumentChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, chunks: List[DocumentChunk]):
        """
        Efficiently adds multiple chunks to the session.
        """
        self.db.add_all(chunks)
        self.db.flush()  # Pushes data to DB, waiting for final Service commit

    def list_by_version(self, version_id: UUID) -> List[DocumentChunk]:
        """
        Returns chunks ordered by their index to reconstruct text flow.
        """
        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_version_id == version_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )