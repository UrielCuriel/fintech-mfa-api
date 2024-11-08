from datetime import  timedelta
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
import jwt

def test_create_access_token():
  subject = "test_user"
  expires_delta = timedelta(minutes=15)
  token = create_access_token(subject, expires_delta)
  
  decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
  assert decoded_token["sub"] == subject
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