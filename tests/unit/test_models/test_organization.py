import pytest
from uuid import uuid4
from datetime import datetime

from app.models.organization import Organization
from tests.test_models import TestOrganization

def test_organization_creation():
    org_id = uuid4()
    
    org = Organization(
        id=org_id,
        name="Test Organization"
    )
    
    assert org.id == org_id
    assert org.name == "Test Organization"

def test_organization_in_database(db_session):
    org_id = str(uuid4())
    org = TestOrganization(
        id=org_id,
        name="Database Test Organization"
    )
    
    db_session.add(org)
    db_session.commit()
    
    saved_org = db_session.query(TestOrganization).filter(TestOrganization.id == org_id).first()
    
    assert saved_org is not None
    assert saved_org.id == org_id
    assert saved_org.name == "Database Test Organization"

def test_organization_unique_name(db_session):
    org1 = TestOrganization(
        id=str(uuid4()),
        name="Unique Name Test"
    )
    db_session.add(org1)
    db_session.commit()
    
    org2 = TestOrganization(
        id=str(uuid4()),
        name="Unique Name Test"
    )
    db_session.add(org2)
    
    with pytest.raises(Exception):
        db_session.commit()
        db_session.rollback()
