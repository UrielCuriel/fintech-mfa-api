from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from app import crud
from app.core import security
from app.schemas import UserCreate
from app.main import app
from app.core.config import settings

client = TestClient(app)


@pytest.fixture
def current_user(session):
    # Mock the current user dependency
    user = crud.create_user(
        session=session,
        user_create=UserCreate(
            email="test@example.com",
            password="password",
        )
    )
    yield user


@pytest.fixture
def token(current_user):
    # Mock the token dependency
    token = security.create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=timedelta(15))
    yield token


def test_update_user_me(session, token):
    response = client.patch(
        f"{settings.API_V_STR}/users/me",
        json={"email": "newemail@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newemail@example.com"


def test_update_password_me(session, token):
    response = client.patch(
        f"{settings.API_V_STR}/users/me/password",
        json={"current_password": "password", "new_password": "newpassword"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"


def test_read_user_me(current_user, token):
    response = client.get(
        f"{settings.API_V_STR}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == current_user.email


def test_delete_user_me(session, token):
    response = client.delete(
        f"{settings.API_V_STR}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


def test_register_user(session):
    response = client.post(
        f"{settings.API_V_STR}/users/signup",
        json={"email": "newuser@example.com", "password": "newpassword"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"
