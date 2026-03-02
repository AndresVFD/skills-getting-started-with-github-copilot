from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    """Deep copy the activities dict before each test and restore it afterwards."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_root_redirect():
    # disable automatic redirect following so we can inspect status & header
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 302)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert "Chess Club" in data


def test_signup_success():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_already_registered():
    existing = activities["Chess Club"]["participants"][0]
    response = client.post("/activities/Chess Club/signup", params={"email": existing})
    assert response.status_code == 400


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup", params={"email": "x@x.com"})
    assert response.status_code == 404


def test_unregister_success():
    email = activities["Chess Club"]["participants"][0]
    response = client.delete("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_participant_not_found():
    response = client.delete("/activities/Chess Club/signup", params={"email": "nosuch@mergington.edu"})
    assert response.status_code == 404


def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent/signup", params={"email": "x@x.com"})
    assert response.status_code == 404
