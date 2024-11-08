import pytest
from fastapi.testclient import TestClient
from app.models import User
from app.main import app

@pytest.fixture
def current_user() -> User:
    """
    Fixture to create an authenticated user for testing.

    Returns:
        User: An instance of the User model with the username "testuser" and email "test@example.com".
    """
    # Tu lógica para crear un usuario autenticado
    return User(username="testuser", email="test@example.com")