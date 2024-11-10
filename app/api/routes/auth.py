import io
import pyotp
import pyqrcode

from fastapi import APIRouter, Depends, HTTPException, Response, logger

from app import crud
from app.api.deps import SessionDep, get_current_user
from app.core import security
from app.core.config import settings


from app.models import User
from app.schemas import Otp, UserPublic

router = APIRouter()


@router.put("/auth/otp/enable")
async def otp_enable(session: SessionDep,
                     otp: Otp,
                     user: User = Depends(get_current_user)):
    """
    Enable OTP for the user
    """
    if user.otp_enabled:
        raise HTTPException(status_code=400, detail="OTP already enabled")
    success = security.verify_otp(otp.totp_code, user.otp_secret)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    user = crud.enable_otp(session=session, db_user=user)
    return UserPublic.model_validate(user)


@router.get("/auth/otp/generate")
def generate_qr_code(session: SessionDep, user: User = Depends(get_current_user)):
    if user.otp_enabled:
        raise HTTPException(status_code=400, detail="OTP already enabled")
    crud.config_otp(session=session, db_user=user)
    totp = pyotp.TOTP(user.otp_secret)
    qr_code = pyqrcode.create(
        totp.provisioning_uri(
            name=user.email, issuer_name=settings.TOTP_ISSUER)
    )
    img_byte_arr = io.BytesIO()
    qr_code.png(img_byte_arr, scale=5)
    img_byte_arr = img_byte_arr.getvalue()
    return Response(content=img_byte_arr, media_type="image/png")
