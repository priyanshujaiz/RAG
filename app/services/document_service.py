import hashlib
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.document_chunk import DocumentChunk
from app.repositories.document_repository import DocumentRepository
from app.repositories.document_version_repository import DocumentVersionRepository
from app.repositories.document_chunk_repository import DocumentChunkRepository

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        # Initialize all three repositories
        self.doc_repo = DocumentRepository(db)
        self.version_repo = DocumentVersionRepository(db)
        # self.chunk_repo = DocumentChunkRepository(db)

    def create_document_metadata(
        self,
        project_id: UUID,
        title: str,
        created_by: UUID,
        file_path: str,
        content_hash: str
    ) -> Document:
        """
        Creates a new logical document, its first version (v1), and splits content into chunks.
        All in one atomic transaction.
        """
        try:
            # 1. Create the Logical Document Container
            new_doc = Document(
                project_id=project_id,
                title=title,
                created_by=created_by
            )
            document = self.doc_repo.create(new_doc) # Adds to session, no commit yet
            
            new_version = DocumentVersion(
                document_id=document.id,
                version_number=1,
                file_path=file_path,
                content_hash=content_hash,
                created_by=created_by
            )
            version = self.version_repo.create(new_version) # Adds to session

            #commit metadata to db
            self.db.commit()
            self.db.refresh(document)
            self.db.refresh(version)
            return document, version

        except Exception as e:
            self.db.rollback()
            raise e

    def create_new_version(
        self,
        document_id: UUID,
        created_by: UUID,
        file_path: str,
        content: str
    ) -> DocumentVersion:
        """
        Adds a NEW version to an existing document. Does NOT update old records.
        """
        try:
            # 1. Determine next version number
            latest_version = self.version_repo.get_latest(document_id)
            next_number = (latest_version.version_number + 1) if latest_version else 1

            # 2. Create the new Version entry
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            new_version = DocumentVersion(
                document_id=document_id,
                version_number=next_number,
                file_path=file_path,
                content_hash=content_hash,
                created_by=created_by
            )
            version = self.version_repo.create(new_version)

            # 3. Create Chunks for THIS version
            chunks = []
            chunk_size = 500
            for i, start in enumerate(range(0, len(content), chunk_size)):
                text_segment = content[start : start + chunk_size]
                chunks.append(
                    DocumentChunk(
                        document_version_id=version.id,
                        chunk_index=i,
                        text=text_segment
                    )
                )

            self.chunk_repo.bulk_create(chunks)

            # 4. Commit
            self.db.commit()
            self.db.refresh(version)
            return version

        except Exception as e:
            self.db.rollback()
            raise e

    def list_project_documents(self, project_id: UUID):
        """
        Simple pass-through to list documents.
        """
        return self.doc_repo.list_by_project(project_id)
        
    def get_document_details(self, document_id: UUID):
        """
        Fetches document metadata.
        """
        return self.doc_repo.get_by_id(document_id)
    

    def list_versions(self, document_id: UUID) -> list[DocumentVersion]:
        """
        Returns all versions for a document.
        """
        return self.version_repo.list_by_document(document_id)