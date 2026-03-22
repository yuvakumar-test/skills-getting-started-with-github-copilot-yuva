import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Use an activity with available spots, like Basketball Team which has empty participants
    response = client.post("/activities/Basketball Team/signup", params={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Basketball Team" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Basketball Team"]["participants"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent Activity/signup", params={"email": "test@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up():
    """Test signup when student is already signed up"""
    # First signup
    client.post("/activities/Basketball Team/signup", params={"email": "duplicate@example.com"})
    # Second signup should fail
    response = client.post("/activities/Basketball Team/signup", params={"email": "duplicate@example.com"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student is already signed up for this activity" in data["detail"]


def test_signup_activity_full():
    """Test signup when activity is full"""
    # Chess Club has max 12, currently 2 participants
    # Add more until full
    for i in range(10):  # 2 already, add 10 more to reach 12
        client.post("/activities/Chess Club/signup", params={"email": f"user{i}@example.com"})
    
    # Now try to add one more
    response = client.post("/activities/Chess Club/signup", params={"email": "overflow@example.com"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Activity is full" in data["detail"]
    pytest.skip("Chess Club is now full, skipping further tests that require it")