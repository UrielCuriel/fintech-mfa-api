from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Form, HTTPException, logger, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from slowapi.errors import RateLimitExceeded
from app.core.security import limiter

import jwt
from sqlmodel import SQLModel

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.schemas import Message, NewPassword, Token, UserPublic
from app.utils import (
    generate_password_reset_token,
    verify_password_reset_token,
)

import app.mails

router = APIRouter()


class TOTPValidationRequest(SQLModel):
    def __init__(self, temp_token: str = Form(...), totp_code: str = Form(...)):
        self.temp_token = temp_token
        self.totp_code = totp_code


@router.post("/login/access-token")
@limiter.limit("5/minute")
def login_access_token(
    session: SessionDep,
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Si el usuario no tiene TOTP activado, generar token de acceso directamente
    if not user.otp_enabled:
        access_token_expires = timedelta(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            {
                "sub": str(user.id),
                "type": "access",
                "totp_required": False
            },
            access_token_expires
        )
        return Token(
            access_token=access_token,
            requires_totp=False,
            message="Login exitoso"
        )

    # Si tiene TOTP activado, generar token temporal
    temp_token_expires = timedelta(
        minutes=settings.TEMP_TOKEN_EXPIRE_MINUTES)
    temp_token = security.create_access_token(
        {
            "sub": user.email,
            "type": "temp_totp",
            "totp_required": True
        },
        temp_token_expires
    )

    return Token(
        temp_token=temp_token,
        requires_totp=True,
        token_type="temp_totp",
        message="Se requiere verificación TOTP"
    )


@router.post("/login/access-token/otp")
@limiter.limit("5/minute")
def login_access_token_otp(
    session: SessionDep,
    request: Request,
    temp_token: Annotated[str, Form()], totp_code: Annotated[str, Form()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        # Decodificar token temporal
        payload = jwt.decode(
            temp_token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "temp_totp":
            raise HTTPException(status_code=401, detail="Token inválido")

        # Obtener usuario y su secreto TOTP

        user = crud.validate_otp(
            session=session, email=username, totp_code=totp_code)

        if not user:
            raise HTTPException(
                status_code=400, detail="Código TOTP inválido"
            )
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        # Generar token de acceso final
        access_token = security.create_access_token({
            "sub": str(user.id),
            "type": "access",
            "totp_verified": True
        }, access_token_expires)

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token temporal expirado. Inicie el proceso nuevamente"
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")


@router.post("/login/test-token", response_model=UserPublic)
def token_test(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if user:
        password_reset_token = generate_password_reset_token(email=email)
        email_data = [
            {
                "email": user.email,
                "data": {
                    "url": f"{settings.FRONTEND_HOST}/reset-password?token={password_reset_token}",
                    "name": user.full_name,
                    "account": {
                        "name": settings.PROJECT_NAME,
                    },
                    "support_email": settings.SUPPORT_EMAIL,
                }
            }
        ]
        app.mails.send_email(
            template_key="password_reset",
            recipients=[{"name": user.full_name, "email": user.email}],
            personalization_data=email_data,
            subject="Password recovery",
        )
    return Message(message="If the email exists, you should receive an email shortly.")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    # Verificar el token de recuperación
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Obtener el usuario por email
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404, detail="The user with this email does not exist in the system.")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Actualizar la contraseña del usuario
    user.hashed_password = get_password_hash(body.new_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    assert security.verify_password(
        body.new_password, user.hashed_password), "Password hashing failed!"

    return Message(message="Password updated successfully")
