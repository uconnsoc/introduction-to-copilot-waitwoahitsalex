"""Tests for the activities list endpoint"""

from fastapi.testclient import TestClient


def test_get_activities_returns_success(client: TestClient):
    """Test that GET /activities returns 200 OK"""
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_returns_all_activities(client: TestClient):
    """Test that GET /activities returns all 9 activities"""
    response = client.get("/activities")
    activities = response.json()
    assert len(activities) == 9


def test_get_activities_has_expected_activity_names(client: TestClient):
    """Test that the response contains all expected activity names"""
    response = client.get("/activities")
    activities = response.json()
    expected_names = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Swimming Club",
        "Art Studio",
        "Drama Club",
        "Debate Team",
        "Science Club"
    ]
    assert set(activities.keys()) == set(expected_names)


def test_activity_has_required_fields(client: TestClient):
    """Test that each activity has the required fields"""
    response = client.get("/activities")
    activities = response.json()
    
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    for activity_name, activity_data in activities.items():
        assert set(activity_data.keys()) == required_fields, \
            f"Activity '{activity_name}' missing required fields"


def test_participants_is_list(client: TestClient):
    """Test that participants field is a list for each activity"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["participants"], list), \
            f"Activity '{activity_name}' participants should be a list"


def test_activity_data_types(client: TestClient):
    """Test that activity fields have correct data types"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_get_activities_chess_club_has_participants(client: TestClient):
    """Test that Chess Club has the expected initial participants"""
    response = client.get("/activities")
    activities = response.json()
    
    chess_club = activities["Chess Club"]
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]
