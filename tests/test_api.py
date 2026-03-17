from datetime import datetime, timedelta
import io

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


def test_export_candidates_csv(client: TestClient):
    client.post("/api/candidates", json={"name": "Export Me", "position": "SRE"})

    response = client.get("/api/candidates-export", params={"format": "csv"})
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "name,position" in response.text
    assert "Export Me" in response.text


def test_import_candidates_csv_with_case_insensitive_headers(client: TestClient):
    existing = client.post("/api/candidates", json={"name": "Base", "position": "ML Engineer"}).json()
    csv_content = (
        "ID,Name,Position,PIPELINE_STAGE,action_required,priority,notes\n"
        f"{existing['id']},Base Updated,ML Engineer,OFFERED,,HIGH,Offer in discussion\n"
        ",New Person,Data Engineer,SCHEDULED,NONE,MEDIUM,Interview fixed\n"
    )

    response = client.post(
        "/api/candidates-import",
        files={"file": ("candidates.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["created"] == 1
    assert payload["updated"] == 1

    all_candidates = client.get("/api/candidates").json()
    assert len(all_candidates) == 2
    updated = [item for item in all_candidates if item["id"] == existing["id"]][0]
    assert updated["name"] == "Base Updated"
    assert updated["pipeline_stage"] == "OFFERED"
    assert updated["action_required"] == "FOLLOW_UP"


def test_import_rejects_unknown_columns(client: TestClient):
    csv_content = "name,position,bad_column\nAlex,Platform Engineer,x\n"

    response = client.post(
        "/api/candidates-import",
        files={"file": ("bad.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
    )

    assert response.status_code == 400
    assert "Unsupported columns" in response.json()["detail"]


def test_clear_candidates_endpoint(client: TestClient):
    client.post("/api/candidates", json={"name": "One", "position": "Platform Engineer"})
    client.post("/api/candidates", json={"name": "Two", "position": "Platform Engineer"})

    clear_response = client.post("/api/candidates-clear")
    assert clear_response.status_code == 200
    assert clear_response.json()["deleted"] == 2

    candidates = client.get("/api/candidates").json()
    assert candidates == []
