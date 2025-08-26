from sqlalchemy.orm import Session
from app.models.user import User
from uuid import UUID

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, name: str, email: str, hashed_password: str, organization_id: UUID, role: str):
    user = User(name=name, email=email, hashed_password=hashed_password, organization_id=organization_id, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()