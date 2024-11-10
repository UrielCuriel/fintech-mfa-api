from datetime import timedelta
import io
import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app  # Importa tu aplicación FastAPI
from app.models import User
from app.crud import create_user, enable_otp
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.schemas import UserCreate  # Asegúrate de tener esta función

client = TestClient(app)


# Mock para obtener el usuario actual sin OTP habilitado
def mock_get_current_user_otp_disabled(session):
    return create_user(session=session, user_create=UserCreate(id=str(uuid.uuid4()), username="testuser", otp_enabled=False, email="test@example.com", password="password123"))


# Mock para obtener el usuario actual con OTP habilitado
def mock_get_current_user_otp_enabled(session):
    return create_user(session=session, user_create=UserCreate(id=str(uuid.uuid4()), username="testuser", otp_enabled=True, email="test@example.com", password="password123"))


# Mock para habilitar OTP
def mock_enable_otp(session, db_user):
    db_user.otp_enabled = True
    return db_user


def get_auth_headers(user):
    """
    Genera un token de acceso y lo incluye en los headers de autorización.
    """
    data = {"sub": str(user.id), "type": "access", "totp_required": False}
    access_expires = timedelta(15)
    access_token = create_access_token(data, access_expires)
    return {"Authorization": f"Bearer {access_token}"}


# Test para habilitar OTP
@patch("app.api.deps.get_current_user", mock_get_current_user_otp_disabled)
@patch("app.crud.enable_otp", mock_enable_otp)
def test_enable_otp(session):
    user = mock_get_current_user_otp_disabled(session)
    headers = get_auth_headers(user)
    response = client.put("/api/v1/auth/otp/enable", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["otp_enabled"] is True


# Test para habilitar OTP cuando ya está habilitado
@patch("app.api.deps.get_current_user", mock_get_current_user_otp_enabled)
def test_enable_otp_already_enabled(session):
    user = mock_get_current_user_otp_enabled(session)
    headers = get_auth_headers(user)
    response = client.put("/api/v1/auth/otp/enable", headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "OTP already enabled"


# Test para generar un código QR
@patch("app.api.deps.get_current_user", mock_get_current_user_otp_disabled)
def test_generate_qr_code(session):
    user = mock_get_current_user_otp_disabled(session)
    headers = get_auth_headers(user)
    response = client.get("/api/v1/auth/otp/generate", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "image/png"
    assert isinstance(response.content, bytes)
    assert len(response.content) > 0
    
# Test para verificar OTP exitoso
@patch("app.api.deps.get_current_user", mock_get_current_user_otp_enabled)
@patch("app.core.security.verify_otp", return_value=True)
def test_verify_otp_success(mock_verify_otp, session):
    user = mock_get_current_user_otp_enabled(session)
    headers = get_auth_headers(user)
    response = client.post("/api/v1/auth/otp/verify", headers=headers, json={"totp_code": "123456"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "OTP verified"
    mock_verify_otp.assert_called_once_with("123456", user.otp_secret)


# Test para verificar OTP fallido
@patch("app.api.deps.get_current_user", mock_get_current_user_otp_enabled)
@patch("app.core.security.verify_otp", return_value=False)
def test_verify_otp_failure(mock_verify_otp, session):
    user = mock_get_current_user_otp_enabled(session)
    headers = get_auth_headers(user)
    response = client.post("/api/v1/auth/otp/verify", headers=headers, json={"totp_code": "123456"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid OTP"
    mock_verify_otp.assert_called_once_with("123456", user.otp_secret)

