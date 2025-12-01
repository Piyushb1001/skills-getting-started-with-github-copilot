import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test cases for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self):
        """Test that activities response contains expected activity names"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = ["Chess Club", "Programming Class", "Basketball Team"]
        for activity in expected_activities:
            assert activity in activities
    
    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field {field}"
    
    def test_participants_is_list(self):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Participants for {activity_name} is not a list"


class TestSignupEndpoint:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_returns_200(self):
        """Test successful signup returns 200"""
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 200
    
    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
    
    def test_signup_for_nonexistent_activity_returns_404(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_duplicate_signup_returns_400(self):
        """Test that duplicate signup returns 400 error"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()
    
    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds participant to participants list"""
        email = "addtest@mergington.edu"
        
        # Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Programming Class"]["participants"])
        
        # Signup
        client.post(f"/activities/Programming%20Class/signup?email={email}")
        
        # Get updated count
        response2 = client.get("/activities")
        updated_count = len(response2.json()["Programming Class"]["participants"])
        
        assert updated_count == initial_count + 1
        assert email in response2.json()["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_returns_200(self):
        """Test successful unregister returns 200"""
        email = "unregister_test@mergington.edu"
        
        # First signup
        client.post(f"/activities/Debate%20Club/signup?email={email}")
        
        # Then unregister
        response = client.delete(f"/activities/Debate%20Club/unregister?email={email}")
        assert response.status_code == 200
    
    def test_unregister_returns_success_message(self):
        """Test that unregister returns a success message"""
        email = "unregister_msg@mergington.edu"
        
        # Signup first
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        
        # Unregister
        response = client.delete(f"/activities/Tennis%20Club/unregister?email={email}")
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_nonexistent_activity_returns_404(self):
        """Test unregister for non-existent activity returns 404"""
        response = client.delete("/activities/NonExistent/unregister?email=test@mergington.edu")
        assert response.status_code == 404
    
    def test_unregister_not_registered_student_returns_404(self):
        """Test unregister for student not in activity returns 404"""
        response = client.delete("/activities/Science%20Olympiad/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_removes_participant_from_activity(self):
        """Test that unregister actually removes participant"""
        email = "remove_test@mergington.edu"
        
        # Signup
        client.post(f"/activities/Painting%20Club/signup?email={email}")
        
        # Get count before unregister
        response1 = client.get("/activities")
        count_before = len(response1.json()["Painting Club"]["participants"])
        
        # Unregister
        client.delete(f"/activities/Painting%20Club/unregister?email={email}")
        
        # Get count after unregister
        response2 = client.get("/activities")
        count_after = len(response2.json()["Painting Club"]["participants"])
        
        assert count_after == count_before - 1
        assert email not in response2.json()["Painting Club"]["participants"]


class TestRootEndpoint:
    """Test cases for GET / endpoint"""
    
    def test_root_returns_redirect(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
