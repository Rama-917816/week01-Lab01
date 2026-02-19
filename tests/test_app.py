import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    initial_state = {
        "Basketball Club": {
            "description": "Team basketball practice and friendly matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis coaching and tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, theater production, and stage performance",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "ryan@mergington.edu"]
        },
        "Science Club": {
            "description": "Experiments, research projects, and STEM exploration",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["nina@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and restore activities
    activities.clear()
    activities.update(initial_state)
    yield
    # Reset after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities(self, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Club" in data
        assert "Tennis Club" in data
        assert len(data) == 9

    def test_activity_structure(self, reset_activities):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_participants_list(self, reset_activities):
        """Test that participants are listed correctly"""
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" in data["Basketball Club"]["participants"]
        assert "lucas@mergington.edu" in data["Drama Club"]["participants"]
        assert "isabella@mergington.edu" in data["Drama Club"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_appears_in_list(self, reset_activities):
        """Test that signup appears in activity list"""
        # Sign up
        client.post(
            "/activities/Basketball%20Club/signup?email=newstudent@mergington.edu"
        )
        
        # Get activities and verify signup
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Basketball Club"]["participants"]

    def test_duplicate_signup_rejected(self, reset_activities):
        """Test that duplicate signups are rejected"""
        # Try to sign up with existing participant
        response = client.post(
            "/activities/Basketball%20Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_to_nonexistent_activity(self, reset_activities):
        """Test signup to nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_multiple_students_can_signup(self, reset_activities):
        """Test that multiple different students can sign up"""
        client.post(
            "/activities/Tennis%20Club/signup?email=student1@mergington.edu"
        )
        client.post(
            "/activities/Tennis%20Club/signup?email=student2@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Tennis Club"]["participants"]
        
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 3  # sarah + 2 new students


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_successful_unregister(self, reset_activities):
        """Test successful unregistration from activity"""
        response = client.delete(
            "/activities/Basketball%20Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, reset_activities):
        """Test that unregister removes participant from list"""
        # Unregister
        client.delete(
            "/activities/Basketball%20Club/unregister?email=alex@mergington.edu"
        )
        
        # Verify removal
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" not in data["Basketball Club"]["participants"]

    def test_unregister_nonexistent_participant(self, reset_activities):
        """Test unregistering a participant who isn't signed up"""
        response = client.delete(
            "/activities/Basketball%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_from_nonexistent_activity(self, reset_activities):
        """Test unregister from nonexistent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_after_unregister(self, reset_activities):
        """Test that student can sign up again after unregistering"""
        # Unregister
        client.delete(
            "/activities/Basketball%20Club/unregister?email=alex@mergington.edu"
        )
        
        # Sign up again
        response = client.post(
            "/activities/Basketball%20Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" in data["Basketball Club"]["participants"]


class TestRoot:
    """Tests for root endpoint redirect"""

    def test_root_redirect(self):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
