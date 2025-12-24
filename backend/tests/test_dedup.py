from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app import models
from app.database import Base
from app.services import dedup


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_strong_match_email(db_session):
    lead = models.Lead(email="test@example.com", first_name="A", last_name="B", source="test")
    db_session.add(lead)
    db_session.commit()
    dup = dedup.find_duplicate(db_session, email="test@example.com", phone=None, first_name="A", last_name="B", city=None, zipcode=None, threshold=0.9)
    assert dup is not None
    assert dup.id == lead.id
