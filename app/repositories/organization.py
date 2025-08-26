from sqlalchemy.orm import Session
from app.models.organization import Organization

def create_organization(db: Session, name: str):
    org = Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

def get_organization_by_name(db: Session, name: str):
    return db.query(Organization).filter(Organization.name == name).first()

def get_all_organizations(db: Session):
    return db.query(Organization).all()