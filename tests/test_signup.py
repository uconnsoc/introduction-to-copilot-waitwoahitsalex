"""Tests for the signup endpoint"""

from fastapi.testclient import TestClient


def test_signup_happy_path(client: TestClient):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": "james@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "james@mergington.edu" in data["message"]
    assert "Basketball Team" in data["message"]


def test_signup_adds_participant_to_activity(client: TestClient):
    """Test that a participant is actually added to the activity"""
    # Sign up a new student
    client.post(
        "/activities/Swimming Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    swimming_club = activities["Swimming Club"]
    
    assert "newstudent@mergington.edu" in swimming_club["participants"]
    assert len(swimming_club["participants"]) == 1


def test_signup_nonexistent_activity_returns_404(client: TestClient):
    """Test that signing up for a non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_returns_400(client: TestClient):
    """Test that signing up twice with the same email returns 400"""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(
        "/activities/Art Studio/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        "/activities/Art Studio/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_existing_participant_returns_400(client: TestClient):
    """Test that an already-registered student cannot sign up again"""
    email = "daniel@mergington.edu"  # Already in Chess Club
    
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_multiple_students_same_activity(client: TestClient):
    """Test that multiple different students can sign up for the same activity"""
    activity_name = "Drama Club"
    emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
    
    for email in emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all students are in the activity
    response = client.get("/activities")
    activities = response.json()
    drama_club = activities[activity_name]
    
    for email in emails:
        assert email in drama_club["participants"]


def test_signup_case_sensitive_activity_name(client: TestClient):
    """Test that activity name is case-sensitive"""
    response = client.post(
        "/activities/chess club/signup",  # lowercase
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404


def test_signup_activity_name_with_spaces(client: TestClient):
    """Test that activity names with spaces work correctly"""
    response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": "hooper@mergington.edu"}
    )
    assert response.status_code == 200
    assert "Basketball Team" in response.json()["message"]


def test_signup_preserves_existing_participants(client: TestClient):
    """Test that signup preserves existing participants"""
    # Get initial state
    response = client.get("/activities")
    chess_club = response.json()["Chess Club"]
    initial_count = len(chess_club["participants"])
    initial_participants = chess_club["participants"].copy()
    
    # Add a new student
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "newchessplayer@mergington.edu"}
    )
    
    # Verify existing participants are still there
    response = client.get("/activities")
    chess_club = response.json()["Chess Club"]
    
    assert len(chess_club["participants"]) == initial_count + 1
    for participant in initial_participants:
        assert participant in chess_club["participants"]
