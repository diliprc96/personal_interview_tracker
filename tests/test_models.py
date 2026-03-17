from datetime import date, datetime, timedelta

import pytest
from pydantic import ValidationError

from app import crud
from app.database import configure_database, get_session_factory, init_db
from app.enums import ActionRequired, Priority
from app.models import Candidate
from app.schemas import CandidateCreate


@pytest.fixture()
def db_session(tmp_path):
    db_file = tmp_path / "unit_test.db"
    configure_database(f"sqlite:///{db_file}")
    init_db()

    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def test_candidate_creation_applies_defaults(db_session):
    candidate = Candidate(name="Alice", position="GenAI Engineer")
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)

    assert candidate.pipeline_stage.value == "TO_BE_SCHEDULED"
    assert candidate.action_required.value == "SCHEDULE"
    assert candidate.priority.value == "MEDIUM"
    assert candidate.created_at is not None
    assert candidate.updated_at is not None


def test_candidate_create_validates_required_fields_and_enums():
    with pytest.raises(ValidationError):
        CandidateCreate(name="", position="GenAI Engineer")

    with pytest.raises(ValidationError):
        CandidateCreate(name="Alice", position="GenAI Engineer", priority="URGENT")


def test_filtering_by_action_and_date_range(db_session):
    now = datetime.now()

    c1 = Candidate(
        name="One",
        position="Backend Engineer",
        action_required=ActionRequired.DECIDE,
        priority=Priority.HIGH,
        next_interview_datetime=now + timedelta(days=1),
        expected_joining_date=date.today() + timedelta(days=20),
    )
    c2 = Candidate(
        name="Two",
        position="Backend Engineer",
        action_required=ActionRequired.NONE,
        priority=Priority.LOW,
        next_interview_datetime=now + timedelta(days=5),
        expected_joining_date=date.today() + timedelta(days=45),
    )

    db_session.add_all([c1, c2])
    db_session.commit()

    filtered_action = crud.list_candidates(db_session, action_required=ActionRequired.DECIDE)
    assert len(filtered_action) == 1
    assert filtered_action[0].name == "One"

    filtered_date = crud.list_candidates(
        db_session,
        next_interview_from=now,
        next_interview_to=now + timedelta(days=2),
    )
    assert len(filtered_date) == 1
    assert filtered_date[0].name == "One"
