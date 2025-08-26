from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.request.organization_request import OrganizationCreateRequest
from app.schemas.response.organization_response import OrganizationResponse
from app.services.organization_service import add_organization, list_organizations
from app.database import get_db
from app.schemas.response.api_response import APIResponse

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/", response_model=APIResponse[OrganizationResponse])
def create_organization_api(
    org_in: OrganizationCreateRequest,
    db: Session = Depends(get_db)
):
    org = add_organization(db, org_in.name)
    return APIResponse(
        code="200",
        message="success",
        result=org
    )

@router.get("/", response_model=APIResponse[list[OrganizationResponse]])
def list_organizations_api(db:Session = Depends(get_db)):
    orgs = list_organizations(db)
    return APIResponse(
        code="200",
        message="success",
        result=orgs
    )