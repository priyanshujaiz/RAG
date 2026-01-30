from uuid import UUID
from sqlalchemy.orm import Session
from app.models.document import Document

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, document: Document) -> Document:
        """
        Adds a document to the session but allows the Service to commit.
        """
        self.db.add(document)
        self.db.flush()  # Generates ID, keeps transaction open
        return document

    def get_by_id(self, document_id: UUID) -> Document | None:
        """
        Fetches a document if it exists and is not deleted.
        """
        return (
            self.db.query(Document)
            .filter(
                Document.id == document_id,
                Document.is_deleted == False
            )
            .first()
        )

    def list_by_project(self, project_id: UUID) -> list[Document]:
        """
        Lists all active documents in a project.
        """
        return (
            self.db.query(Document)
            .filter(
                Document.project_id == project_id,
                Document.is_deleted == False
            )
            .all()
        )