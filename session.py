from fastapi import HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
import bcrypt

from main import app
from utils import *

import schemas
import db
import settings

class Settings(BaseModel):
    authjwt_secret_key: str = settings.jwt_secret
    authjwt_token_location: set = {"cookies"}
    
    authjwt_cookie_csrf_protect: bool = False
    
    #authjwt_cookie_secure: bool = False
    #authjwt_cookie_csrf_protect: bool = True

@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code = exc.status_code, content = {"detail": exc.message})

# Login
@app.post("/session", status_code = 201)
def f_session_post(data: schemas.SessionPost, Authorize: AuthJWT = Depends()):
    if not user_exists(data.username):
        raise HTTPException(status_code = 401, detail = "Bad credentials")

    hash = user_get(data.username).password_hash.encode("ascii", "strict")
    password = data.password.encode("ascii", "strict")
    
    if not bcrypt.checkpw(password, hash):
        raise HTTPException(status_code = 401, detail = "Bad credentials")

    access_token = Authorize.create_access_token(subject = data.username)
    refresh_token = Authorize.create_refresh_token(subject = data.username)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}

# Refresh access token
@app.put('/session', status_code = 200)
def f_session_put(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    current_username = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject = current_username)
    Authorize.set_access_cookies(new_access_token)
    return {"access_token": new_access_token}

# Logout
@app.delete('/session', status_code = 200)
def f_session_delete(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    return {"msg": "Successfully logout"}


