from uuid import UUID
from sqlalchemy.orm import Session
from app.models.document_version import DocumentVersion

class DocumentVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, version: DocumentVersion) -> DocumentVersion:
        self.db.add(version)
        self.db.flush() 
        return version

    def get_latest(self, document_id: UUID) -> DocumentVersion | None:
        """
        Returns the version with the highest version_number.
        """
        return (
            self.db.query(DocumentVersion)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .first()
        )

    def list_by_document(self, document_id: UUID) -> list[DocumentVersion]:
        """
        Returns full history ordered by version number (1, 2, 3...).
        """
        return (
            self.db.query(DocumentVersion)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.asc())
            .all()
        )
    def get_by_id(self, id: UUID) -> DocumentVersion | None:
        return self.db.query(DocumentVersion).filter(DocumentVersion.id == id).first()
