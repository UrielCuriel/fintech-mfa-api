import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_otp, verify_password, generate_otp_secret
from app.models import User
from app.schemas import UserCreate, UserUpdate
from typing import Union


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={
            "hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    if "otp_enabled" in user_data:
        if user_data["otp_enabled"]:
            extra_data["otp_secret"] = generate_otp_secret()
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def config_otp(*, session: Session, db_user: User) -> User:
    user_data = db_user.model_dump()
    extra_data = {"otp_secret": generate_otp_secret()}
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def enable_otp(*, session: Session, db_user: User) -> User:
    user_data = db_user.model_dump()
    extra_data = {"otp_enabled": True}
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_otp_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user.otp_enabled


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None

    return db_user


def validate_otp(*, session: Session, email: str, totp_code: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if db_user.otp_enabled:
        if not totp_code:
            return None
        if not db_user.otp_secret:
            return None
        if not verify_otp(totp_code, db_user.otp_secret):
            return None
    return db_user
