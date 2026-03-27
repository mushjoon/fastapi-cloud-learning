import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from main import app

# Create test client
client = TestClient(app)

# Test data
test_user = {
    "name": "Test User",
    "email": "test@example.com",
    "age": 25
}

class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check(self):
        """Test GET /health returns 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        # Your health endpoint also returns database status
        assert "database" in data


class TestUsersEndpoints:
    """Test all CRUD operations on /users endpoint"""
    
    @patch('main.get_db_connection')
    def test_create_user(self, mock_db):
        """Test POST /users creates a new user"""
        # Mock cursor
        mock_cursor = Mock()
        mock_cursor.lastrowid = 123
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        
        # Set up the mock to return our connection
        mock_db.return_value = mock_connection
        
        # Make request
        response = client.post("/users", json=test_user)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 123
        assert data["message"] == "User created successfully"
        
        # Verify database methods were called
        mock_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
    
    @patch('main.get_db_connection')
    def test_get_all_users(self, mock_db):
        """Test GET /users returns list of users"""
        # Mock cursor with dictionary=True (returns dicts, not tuples)
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "User One", "email": "user1@example.com", "age": 30},
            {"id": 2, "name": "User Two", "email": "user2@example.com", "age": 25}
        ]
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value = mock_connection
        
        # Make request
        response = client.get("/users")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        # Your API returns {"users": [...], "count": 2}
        assert "users" in data
        assert "count" in data
        assert len(data["users"]) == 2
        assert data["count"] == 2
        assert data["users"][0]["name"] == "User One"
        assert data["users"][1]["name"] == "User Two"

    @patch('main.get_db_connection')
    def test_get_user_by_id(self, mock_db):
        """Test GET /users/{id} returns specific user"""
        # Mock cursor with dictionary=True (returns dict, not tuple)
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            "id": 1, 
            "name": "Test User", 
            "email": "test@example.com", 
            "age": 25
        }
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value = mock_connection
        
        # Make request
        response = client.get("/users/1")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert data["age"] == 25

    
    @patch('main.get_db_connection')
    def test_get_user_not_found(self, mock_db):
        """Test GET /users/{id} with non-existent user returns 404"""
        # Mock cursor with no result
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value = mock_connection
        
        # Make request
        response = client.get("/users/999")
        
        # Assertions
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}
    
    @patch('main.get_db_connection')
    def test_update_user(self, mock_db):
        """Test PUT /users/{id} updates user"""
        # Mock cursor with rowcount
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value = mock_connection
        
        # Updated data
        updated_user = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "age": 30
        }
        
        # Make request
        response = client.put("/users/1", json=updated_user)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User updated successfully"
        
        # Verify update was called
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    @patch('main.get_db_connection')
    def test_update_user_not_found(self, mock_db):
        """Test PUT /users/{id} with non-existent user returns 404"""
        # Mock cursor with no rows affected
        mock_cursor = Mock()
        mock_cursor.rowcount = 0
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value = mock_connection
        
        # Make request
        response = client.put("/users/999", json=test_user)
        
        # Assertions
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}
    
    @patch('main.get_db_connection')
    def test_delete_user(self, mock_db):
        """Test DELETE /users/{id} deletes user"""
        # Mock cursor with rowcount
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value = mock_connection
        
        # Make request
        response = client.delete("/users/1")
        
        # Assertions
        assert response.status_code == 200
        assert response.json() == {"message": "User deleted successfully"}
        
        # Verify delete was called
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    @patch('main.get_db_connection')
    def test_delete_user_not_found(self, mock_db):
        """Test DELETE /users/{id} with non-existent user returns 404"""
        # Mock cursor with no rows affected
        mock_cursor = Mock()
        mock_cursor.rowcount = 0
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db.return_value = mock_connection
        
        # Make request
        response = client.delete("/users/999")
        
        # Assertions
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}



