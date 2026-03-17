from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture()
def client(tmp_path):
    db_file = tmp_path / "api_test.db"
    app = create_app(f"sqlite:///{db_file}")
    with TestClient(app) as test_client:
        yield test_client


def test_create_candidate_happy_path(client: TestClient):
    response = client.post(
        "/api/candidates",
        json={
            "name": "Jordan",
            "position": "GenAI Engineer",
            "priority": "HIGH",
            "notes": "Strong backend profile",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["pipeline_stage"] == "TO_BE_SCHEDULED"
    assert payload["action_required"] == "SCHEDULE"
    assert payload["priority"] == "HIGH"


def test_create_candidate_validation_error(client: TestClient):
    response = client.post(
        "/api/candidates",
        json={"position": "GenAI Engineer"},
    )

    assert response.status_code == 422


def test_patch_and_filter_candidates(client: TestClient):
    create_resp = client.post(
        "/api/candidates",
        json={"name": "Riya", "position": "ML Engineer"},
    )
    candidate_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/api/candidates/{candidate_id}",
        json={
            "pipeline_stage": "INTERVIEW_COMPLETED",
            "action_required": "DECIDE",
            "notes": "Needs architecture discussion",
        },
    )

    assert patch_resp.status_code == 200
    patched_payload = patch_resp.json()
    assert patched_payload["action_required"] == "DECIDE"

    list_resp = client.get("/api/candidates", params={"action_required": "DECIDE"})
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_get_candidates_invalid_enum(client: TestClient):
    response = client.get("/api/candidates", params={"action_required": "DO_NOW"})
    assert response.status_code == 422


def test_next_interview_date_filters(client: TestClient):
    dt_soon = (datetime.now() + timedelta(days=1)).replace(microsecond=0).isoformat()
    dt_later = (datetime.now() + timedelta(days=8)).replace(microsecond=0).isoformat()

    first = client.post("/api/candidates", json={"name": "Soon", "position": "SRE"}).json()
    second = client.post("/api/candidates", json={"name": "Later", "position": "SRE"}).json()

    client.patch(f"/api/candidates/{first['id']}", json={"next_interview_datetime": dt_soon})
    client.patch(f"/api/candidates/{second['id']}", json={"next_interview_datetime": dt_later})

    response = client.get(
        "/api/candidates",
        params={
            "next_interview_from": datetime.now().replace(microsecond=0).isoformat(),
            "next_interview_to": (datetime.now() + timedelta(days=3)).replace(microsecond=0).isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Soon"
