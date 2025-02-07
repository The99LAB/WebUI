from jose import JWTError, jwt
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import pam
from settings import SettingsManager

SECRET_KEY = "secret!"
ALGORITHM = "HS256"
settings_manager = SettingsManager()

def check_auth(request: Request):
    try:
        token = request.headers['Authorization'].split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        # check expiration
        expires = payload.get("exp")
        if expires is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        expires_datetime = datetime.utcfromtimestamp(expires)
        if datetime.utcnow() > expires_datetime:
            raise HTTPException(status_code=401, detail="Authentication token expired")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

def login(username, password):
    if pam.authenticate(username, password):
        expire_time_seconds = int(settings_manager.get_setting("login_token_expire").value)
        expires_delta = timedelta(seconds=expire_time_seconds)
        expire = datetime.utcnow() + expires_delta
        token = jwt.encode({"username": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM, )
        print("auth success")
        return token
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

# check auth by token
def check_auth_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            return False
        expires = payload.get("exp")
        if expires is None:
            return False
        expires_datetime = datetime.utcfromtimestamp(expires)
        if datetime.utcnow() > expires_datetime:
            return False
        return True
    except JWTError:
        return False