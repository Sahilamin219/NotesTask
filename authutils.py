from datetime import datetime, timedelta
import jwt
from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
# Function to get the current user from the JWT token

async def get_current_user_from_header(token: str = Depends(oauth2_scheme)): # You created a function that depends on oauth2_scheme
  
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], verify=False)
        return payload['sub']
    except Exception as e:
        print("Error",e)

def validate_user(username, password):
    pass

