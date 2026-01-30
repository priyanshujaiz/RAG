from sqlalchemy.orm import Session
from app.models.user import User
from uuid import UUID

class UserRepository:
    def get_by_email(self,db: Session, email:str)-> User | None:
        return db.query(User).filter(User.email ==email).first()


    def create(self, db: Session, user:User)-> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_id(self, db: Session, user_id: UUID):
        return db.query(User).filter(User.id == user_id).first()


