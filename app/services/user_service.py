from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.security import hash_password, verify_password

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def register_user(self, db: Session, email: str, password: str) -> User:
        if self.repo.get_by_email(db, email):
            raise ValueError("Email already registered")

        user = User(
            email=email,
            hashed_password=hash_password(password)
        )
        return self.repo.create(db, user)

    def authenticate_user(self, db: Session, email: str, password: str) -> User | None:
        user = self.repo.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
