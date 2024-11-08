import pytest
from sqlmodel import Session
from app.crud import create_user, update_user, get_user_by_email, authenticate
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def test_create_user(session: Session):
  user_create = UserCreate(email="test@example.com", password="password123", username="test@example.com")
  user = create_user(session=session, user_create=user_create)
  assert user.email == "test@example.com"
  assert user.hashed_password != "password123"
  assert verify_password("password123", user.hashed_password)

def test_update_user(session: Session):
  user_create = UserCreate(email="test@example.com", password="password123", username="test@example.com")
  user = create_user(session=session, user_create=user_create)
  previous_hashed_password = str(user.hashed_password)
  user_update = UserUpdate(password="newpassword123")
  updated_user = update_user(session=session, db_user=user, user_in=user_update)
  assert updated_user.hashed_password != previous_hashed_password
  assert verify_password("newpassword123", updated_user.hashed_password)

def test_get_user_by_email(session: Session):
  user_create = UserCreate(email="test@example.com", password="password123", username="test@example.com")
  create_user(session=session, user_create=user_create)
  user = get_user_by_email(session=session, email="test@example.com")
  assert user is not None
  assert user.email == "test@example.com"

def test_authenticate(session: Session):
  user_create = UserCreate(email="test@example.com", password="password123", username="test@example.com")
  create_user(session=session, user_create=user_create)
  user = authenticate(session=session, email="test@example.com", password="password123")
  assert user is not None
  assert user.email == "test@example.com"
  assert authenticate(session=session, email="test@example.com", password="wrongpassword") is None