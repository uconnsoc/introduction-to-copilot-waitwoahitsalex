"""Tests for the unregister endpoint"""

from fastapi.testclient import TestClient


def test_unregister_happy_path(client: TestClient):
    """Test successful unregister from an activity"""
    email = "michael@mergington.edu"  # Already in Chess Club
    
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert email in data["message"]
    assert "Chess Club" in data["message"]


def test_unregister_removes_participant(client: TestClient):
    """Test that unregister actually removes the participant"""
    email = "daniel@mergington.edu"  # In Chess Club
    
    # Verify participant is initially in activity
    response = client.get("/activities")
    assert email in response.json()["Chess Club"]["participants"]
    
    # Unregister
    client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    
    # Verify participant is removed
    response = client.get("/activities")
    assert email not in response.json()["Chess Club"]["participants"]


def test_unregister_nonexistent_activity_returns_404(client: TestClient):
    """Test that unregistering from a non-existent activity returns 404"""
    response = client.delete(
        "/activities/Nonexistent Club/unregister",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up_returns_400(client: TestClient):
    """Test that unregistering when not signed up returns 400"""
    response = client.delete(
        "/activities/Basketball Team/unregister",  # No participants
        params={"email": "neverjoined@mergington.edu"}
    )
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_from_activity_with_participants(client: TestClient):
    """Test unregistering from an activity that has other participants"""
    email_to_remove = "john@mergington.edu"  # In Gym Class
    
    # Get initial state
    response = client.get("/activities")
    gym_class = response.json()["Gym Class"]
    initial_count = len(gym_class["participants"])
    
    # Unregister one student
    response = client.delete(
        "/activities/Gym Class/unregister",
        params={"email": email_to_remove}
    )
    assert response.status_code == 200
    
    # Verify participant count decreased
    response = client.get("/activities")
    gym_class = response.json()["Gym Class"]
    assert len(gym_class["participants"]) == initial_count - 1
    assert email_to_remove not in gym_class["participants"]
    
    # Verify other participants are still there
    assert "olivia@mergington.edu" in gym_class["participants"]


def test_unregister_last_participant(client: TestClient):
    """Test unregistering the last participant from an activity"""
    email = "emma@mergington.edu"  # In Programming Class with sophia
    
    # First unregister emma's classmate sophia
    client.delete(
        "/activities/Programming Class/unregister",
        params={"email": "sophia@mergington.edu"}
    )
    
    # Now unregister emma (the last participant)
    response = client.delete(
        "/activities/Programming Class/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify activity now has no participants
    response = client.get("/activities")
    programming_class = response.json()["Programming Class"]
    assert len(programming_class["participants"]) == 0


def test_unregister_case_sensitive_activity_name(client: TestClient):
    """Test that activity name is case-sensitive for unregister"""
    response = client.delete(
        "/activities/chess club/unregister",  # lowercase
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 404


def test_unregister_cannot_unregister_twice(client: TestClient):
    """Test that you cannot unregister a student twice"""
    email = "michael@mergington.edu"
    
    # First unregister should succeed
    response1 = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second unregister should fail
    response2 = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email}
    )
    assert response2.status_code == 400
    assert "not signed up" in response2.json()["detail"]


def test_unregister_then_signup_again(client: TestClient):
    """Test that a student can unregister and then sign up again"""
    email = "daniel@mergington.edu"
    activity = "Chess Club"
    
    # Unregister
    response1 = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Sign up again
    response2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response2.status_code == 200
    
    # Verify they're back in the activity
    response = client.get("/activities")
    assert email in response.json()[activity]["participants"]


def test_unregister_with_whitespace_in_email(client: TestClient):
    """Test unregister with email parameter (basic validation)"""
    # The app doesn't validate email format, so this should just work
    response = client.delete(
        "/activities/Basketball Team/unregister",
        params={"email": ""}
    )
    # Empty string is not a participant, so 400
    assert response.status_code == 400
