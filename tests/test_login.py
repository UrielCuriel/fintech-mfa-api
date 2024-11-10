from datetime import timedelta
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app import crud
from app.crud import create_user
from app.main import app
from app.api.deps import get_db
from app.models import User
from app.core.security import get_password_hash, create_access_token, verify_password
from app.schemas import NewPassword, UserCreate
from unittest.mock import patch

from app.utils import generate_password_reset_token


client = TestClient(app)


@pytest.fixture
def test_user(session: Session):
    """Crear un usuario para las pruebas."""
    return create_user(session=session, user_create=UserCreate(id=str(uuid.uuid4()), otp_enabled=False, email="test@example.com", password="password123"))


def test_login_access_token(test_user):
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["requires_totp"] is False


def test_login_access_token_wrong_password(test_user):
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_access_token_with_totp(session, test_user):
    test_user.otp_enabled = True
    session.add(test_user)
    session.commit()

    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "temp_token" in data
    assert data["requires_totp"] is True


def test_login_access_token_otp(session, test_user):
    temp_token = create_access_token(
        {"sub": test_user.email, "type": "temp_totp", "totp_required": True},
        expires_delta=timedelta(minutes=5),
    )
    with patch("app.crud.validate_otp") as mock_validate_otp:
        mock_validate_otp.return_value = test_user
        response = client.post(
            "/api/v1/login/access-token/otp",
            data={"temp_token": temp_token, "totp_code": "123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


def test_token_test(test_user):
    token = create_access_token(
        {"sub": str(test_user.id), "type": "access"}, expires_delta=timedelta(minutes=5))
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/login/test-token", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


@patch("app.mails.send_email")
def test_password_recovery(mock_send_email, test_user):
    response = client.post(f"/api/v1/password-recovery/{test_user.email}")
    assert response.status_code == 200
    assert response.json()[
        "message"] == "If the email exists, you should receive an email shortly."
    mock_send_email.assert_called_once()


def test_reset_password(session, test_user):
    token = generate_password_reset_token(test_user.email)
    new_password = "newpassword123"
    response = client.post(
        "/api/v1/reset-password/",
        json={"token": token, "new_password": new_password},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

    
    # Obtener el usuario nuevamente para verificar si la contraseña fue actualizada
    updated_user = crud.get_user_by_email(session=session, email=test_user.email)
    
    # Refrescar la instancia del usuario para asegurarse de que tenga los datos más recientes
    session.refresh(updated_user)
    
    # Verificar que la nueva contraseña sea válida
    # Verificar que el usuario puede autenticarse con la nueva contraseña
    assert verify_password(new_password, updated_user.hashed_password)
