from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

from app.models import User
from app.utils import generate_password_reset_token

client = TestClient(app)


def test_login_access_token_success():
    with patch("app.crud.authenticate") as mock_authenticate, \
            patch("app.core.security.create_access_token") as mock_create_access_token:
        mock_authenticate.return_value = type(
            "User", (), {"id": 1, "is_active": True})
        mock_create_access_token.return_value = "test_token"

        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "test_password"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "access_token": "test_token", "token_type": "bearer"}


def test_login_access_token_incorrect_credentials():
    with patch("app.crud.authenticate") as mock_authenticate:
        mock_authenticate.return_value = None

        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com",
                  "password": "wrong_password"},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Incorrect email or password"}


def test_login_access_token_inactive_user():
    with patch("app.crud.authenticate") as mock_authenticate:
        mock_authenticate.return_value = type(
            "User", (), {"id": 1, "is_active": False})

        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "test_password"},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Inactive user"}


def test_recover_password():
    with patch("app.crud.get_user_by_email") as mock_get_user_by_email, \
            patch("app.utils.generate_password_reset_token") as mock_generate_password_reset_token, \
            patch("app.mails.send_email") as mock_send_email:
        mock_get_user_by_email.return_value = User(
            username="XXXXXXXXX", email="test@example.com", is_active=True)
        mock_generate_password_reset_token.return_value = "test_token"
        mock_send_email.return_value = None

        response = client.post("/api/v1/password-recovery/test@example.com")

        assert response.status_code == 200
        assert response.json() == {
            "message": "If the email exists, you should receive an email shortly."}


def test_reset_password_success():
    user_email = "test@example.com"
    token = generate_password_reset_token(email=user_email)
    with patch("app.utils.verify_password_reset_token") as mock_verify_password_reset_token, \
            patch("app.crud.get_user_by_email") as mock_get_user_by_email, \
            patch("app.core.security.get_password_hash") as mock_get_password_hash, \
            patch("app.api.deps.SessionDep") as mock_session:
        mock_verify_password_reset_token.return_value = user_email
        mock_get_user_by_email.return_value = User(
            email=user_email, is_active=True, username="test_user")
        mock_get_password_hash.return_value = "hashed_password"

        response = client.post(
            "/api/v1/reset-password/",
            json={"token": token, "new_password": "new_password"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Password updated successfully"}


def test_reset_password_invalid_token():
    with patch("app.utils.verify_password_reset_token") as mock_verify_password_reset_token:
        mock_verify_password_reset_token.return_value = None

        response = client.post(
            "/api/v1/reset-password/",
            json={"token": "invalid_token", "new_password": "new_password"},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid token"}


def test_reset_password_user_not_found():
    user_email = "test@example.com"
    token = generate_password_reset_token(email=user_email)
    with patch("app.utils.verify_password_reset_token") as mock_verify_password_reset_token, \
            patch("app.crud.get_user_by_email") as mock_get_user_by_email:
        mock_verify_password_reset_token.return_value = "test@example.com"
        mock_get_user_by_email.return_value = None

        response = client.post(
            "/api/v1/reset-password/",
            json={"token": token, "new_password": "new_password"},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "The user with this email does not exist in the system."}


def test_reset_password_inactive_user():
    user_email = "test@example.com"
    token = generate_password_reset_token(email=user_email)
    with patch("app.utils.verify_password_reset_token") as mock_verify_password_reset_token, \
            patch("app.crud.get_user_by_email") as mock_get_user_by_email:
        mock_verify_password_reset_token.return_value = user_email
        mock_get_user_by_email.return_value = type(
            "User", (), {"is_active": False})

        response = client.post(
            "/api/v1/reset-password/",
            json={"token": token, "new_password": "new_password"},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Inactive user"}
