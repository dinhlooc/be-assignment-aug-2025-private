import pytest
from uuid import uuid4
from unittest.mock import MagicMock, patch

from app.services.organization_service import add_organization, list_organizations
from app.core.exceptions import OrganizationNameExistsException
from app.models.organization import Organization
from app.schemas.response.organization_response import OrganizationResponse

def test_add_organization_success(db_session):
    org_name = f"Test Org {uuid4()}"
    result = add_organization(db_session, org_name)
    assert result is not None
    assert isinstance(result, OrganizationResponse)
    assert result.name == org_name
    assert result.id is not None

def test_add_organization_name_exists(db_session, test_organization):
    existing_name = test_organization.name
    with pytest.raises(OrganizationNameExistsException):
        add_organization(db_session, existing_name)

def test_list_organizations(db_session, test_organization):
    result = list_organizations(db_session)
    assert result is not None
    assert isinstance(result, list)
    assert len(result) >= 1
    org_ids = [str(org.id) for org in result]
    test_org_id = str(test_organization.id)
    assert test_org_id in org_ids
    org_names = [org.name for org in result]
    assert test_organization.name in org_names
