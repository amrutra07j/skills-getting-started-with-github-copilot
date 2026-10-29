import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = copy.deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app, follow_redirects=False) as test_client:
        yield test_client


def test_root_redirects_to_static_index(client):
    response = client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == app_module.activities


def test_signup_adds_participant(client):
    email = "student@mergington.edu"

    response = client.post(
        "/activities/Basketball Club/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Basketball Club"
    }
    assert email in app_module.activities["Basketball Club"]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    email = "student@mergington.edu"
    client.post("/activities/Art Club/signup", params={"email": email})

    response = client.post("/activities/Art Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_remove_participant_removes_signup(client):
    email = "john@mergington.edu"

    response = client.delete(
        "/activities/Gym Class/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Gym Class"}
    assert email not in app_module.activities["Gym Class"]["participants"]


def test_remove_participant_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_returns_not_found_for_unsigned_student(client):
    response = client.delete(
        "/activities/Art Club/signup", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }