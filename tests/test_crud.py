from unittest.mock import patch
import pytest
from sqlmodel import Session
from app.crud import create_user, update_user, get_user_by_email, authenticate, get_otp_user_by_email, enable_otp, validate_otp
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
import pyotp


def test_create_user(session: Session):
    user_create = UserCreate(email="test@example.com",
                             password="password123", username="test@example.com")
    user = create_user(session=session, user_create=user_create)
    assert user.email == "test@example.com"
    assert user.hashed_password != "password123"
    assert verify_password("password123", user.hashed_password)


def test_update_user(session: Session):
    user_create = UserCreate(email="test@example.com",
                             password="password123", username="test@example.com")
    user = create_user(session=session, user_create=user_create)
    previous_hashed_password = str(user.hashed_password)
    user_update = UserUpdate(password="newpassword123")
    updated_user = update_user(
        session=session, db_user=user, user_in=user_update)
    assert updated_user.hashed_password != previous_hashed_password
    assert verify_password("newpassword123", updated_user.hashed_password)


def test_get_user_by_email(session: Session):
    user_create = UserCreate(email="test@example.com",
                             password="password123", username="test@example.com")
    create_user(session=session, user_create=user_create)
    user = get_user_by_email(session=session, email="test@example.com")
    assert user is not None
    assert user.email == "test@example.com"


def test_authenticate(session: Session):
    user_create = UserCreate(email="test@example.com",
                             password="password123", username="test@example.com")
    create_user(session=session, user_create=user_create)
    user = authenticate(
        session=session, email="test@example.com", password="password123")
    assert user is not None
    assert user.email == "test@example.com"
    assert authenticate(session=session, email="test@example.com",
                        password="wrongpassword") is None

def test_enable_otp(session: Session):
    user_create = UserCreate(email="test@example.com",
                             password="password123", username="text@example.com")
    user = create_user(session=session, user_create=user_create)
    enable_otp(session=session, db_user=user)
    assert user.otp_enabled == True

def test_get_otp_user_by_email(session: Session):
    user_create = UserCreate(email="test@example.com",
                             password="password123", username="test@example.com", otp_enabled=True)
    user = create_user(session=session, user_create=user_create)
    is_otp_enabled = get_otp_user_by_email(session=session, email="test@example.com")
    assert is_otp_enabled == True
    
def test_validate_otp(session: Session):
    user_create = UserCreate(email="test@example.com",
                                password="password123", username="test@example.com", otp_enabled=True)
    user = create_user(session=session, user_create=user_create)
    enable_otp(session=session, db_user=user)
    
    # Generate a valid TOTP code
    totp = pyotp.TOTP(user.otp_secret)
    valid_totp_code = totp.now()
    
    # Test with valid TOTP code
    validated_user = validate_otp(session=session, email="test@example.com", totp_code=valid_totp_code)
    assert validated_user is not None
    assert validated_user.email == "test@example.com"
    
    # Test with invalid TOTP code
    invalid_totp_code = "123456"
    validated_user = validate_otp(session=session, email="test@example.com", totp_code=invalid_totp_code)
    assert validated_user is None
    
    # Test with no TOTP code
    validated_user = validate_otp(session=session, email="test@example.com", totp_code="")
    assert validated_user is None
    
    # Test with user not having OTP enabled
    user_create = UserCreate(email="nootp@example.com",
                                password="password123", username="nootp@example.com", otp_enabled=False)
    user = create_user(session=session, user_create=user_create)
    validated_user = validate_otp(session=session, email="nootp@example.com", totp_code=valid_totp_code)
    assert validated_user is not None
    assert validated_user.email == "nootp@example.com"

