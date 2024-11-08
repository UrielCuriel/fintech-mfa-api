import uuid
from jwt import InvalidTokenError
import pytest
from fastapi import HTTPException, status
from sqlmodel import Session
from unittest.mock import MagicMock, patch
from app.api.deps import get_current_user, get_current_active_superuser
from app.models import User
from app.schemas import TokenPayload

@pytest.fixture
def session():
  return MagicMock(spec=Session)

@pytest.fixture
def token():
  return "test_token"

@pytest.fixture
def user():
  return User(id=str(uuid.uuid4()), is_active=True, is_superuser=False)

@pytest.fixture
def superuser():
  return User(id=str(uuid.uuid4()), is_active=True, is_superuser=True)

def test_get_current_user_valid_token(session, token, user):
  with patch("app.api.deps.jwt.decode", return_value={"sub": user.id}), \
     patch("app.api.deps.TokenPayload", return_value=TokenPayload(sub=user.id)), \
     patch.object(session, "get", return_value=user):
    result = get_current_user(session, token)
    assert result == user

def test_get_current_user_invalid_token(session, token):
  with patch("app.api.deps.jwt.decode", side_effect=InvalidTokenError):
    with pytest.raises(HTTPException) as exc_info:
      get_current_user(session, token)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

def test_get_current_user_user_not_found(session, token):
  with patch("app.api.deps.jwt.decode", return_value={"sub": str(uuid.uuid4())}), \
     patch("app.api.deps.TokenPayload", return_value=TokenPayload(sub=str(uuid.uuid4()))), \
     patch.object(session, "get", return_value=None):
    with pytest.raises(HTTPException) as exc_info:
      get_current_user(session, token)
    assert exc_info.value.status_code == 404

def test_get_current_user_inactive_user(session, token, user):
  user.is_active = False
  with patch("app.api.deps.jwt.decode", return_value={"sub": user.id}), \
     patch("app.api.deps.TokenPayload", return_value=TokenPayload(sub=user.id)), \
     patch.object(session, "get", return_value=user):
    with pytest.raises(HTTPException) as exc_info:
      get_current_user(session, token)
    assert exc_info.value.status_code == 400

def test_get_current_active_superuser_valid_superuser(superuser):
  result = get_current_active_superuser(superuser)
  assert result == superuser

def test_get_current_active_superuser_not_superuser(user):
  with pytest.raises(HTTPException) as exc_info:
    get_current_active_superuser(user)
  assert exc_info.value.status_code == 403