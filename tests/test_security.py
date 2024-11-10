from datetime import  timedelta
import uuid
from app.core.security import create_access_token, verify_password, get_password_hash, generate_otp_secret, verify_otp
from app.core.config import settings
import pyotp
import jwt

def test_create_access_token():
  data = {"sub": str(uuid.uuid4()), "type": "access", "totp_required": False}
  expires_delta = timedelta(minutes=15)
  token = create_access_token(data, expires_delta)
  
  decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
  assert decoded_token["sub"] == data["sub"]
  assert decoded_token["type"] == data["type"]
  assert decoded_token["totp_required"] == data["totp_required"]
  assert "exp" in decoded_token

def test_verify_password():
  plain_password = "test_password"
  hashed_password = get_password_hash(plain_password)
  
  assert verify_password(plain_password, hashed_password) == True
  assert verify_password("wrong_password", hashed_password) == False

def test_get_password_hash():
  password = "test_password"
  hashed_password = get_password_hash(password)
  
  assert hashed_password != password
  assert verify_password(password, hashed_password) == True

def test_generate_otp_secret():
    secret = generate_otp_secret()
    assert len(secret) == 32

def test_verify_otp_success():
  secret = "JBSWY3DPEHPK3PXP"
  totp = pyotp.TOTP(secret)
  token = totp.now()
  
  assert verify_otp(token, secret) == True
