from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["description"] == (
        "Learn strategies and compete in chess tournaments"
    )
    assert "michael@mergington.edu" in response.json()["Chess Club"]["participants"]


def test_signup_adds_participant_to_activity():
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_unknown_activity_returns_not_found():
    response = client.post("/activities/Unknown%20Club/signup?email=student%40mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_participant_returns_bad_request():
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael%40mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_requires_email():
    response = client.post("/activities/Chess%20Club/signup")

    assert response.status_code == 422


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_unknown_activity_returns_not_found():
    response = client.delete(
        "/activities/Unknown%20Club/unregister?email=student%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_nonparticipant_returns_bad_request():
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=student%40mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_requires_email():
    response = client.delete("/activities/Chess%20Club/unregister")

    assert response.status_code == 422