from sqlalchemy.orm import Session
from app.repositories.organization import create_organization, get_all_organizations
from app.schemas.response.organization_response import OrganizationResponse
from app.core.exceptions import OrganizationNameExistsException
from app.repositories.organization import get_organization_by_name
def add_organization(db: Session, name: str) -> OrganizationResponse:
    if get_organization_by_name(db, name):
        raise OrganizationNameExistsException()
    org = create_organization(db, name)
    return OrganizationResponse.from_orm(org)

def list_organizations(db: Session) -> list[OrganizationResponse]:
    orgs = get_all_organizations(db)
    return [OrganizationResponse.from_orm(org) for org in orgs]