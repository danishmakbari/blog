from fastapi import HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

import bcrypt

from main import app
import models
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

@app.get('/users/me')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()

    return {"username": current_user}

@app.post("/users/signup", status_code = 201)
def signup(user_data: schemas.UserSignup):
    password = user_data.password.encode("ascii", "strict")
    hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode()
    
    user = models.User(
            email = user_data.email,
            username = user_data.username,
            password_hash = hash,
            blacklist = False,
            admin_role = False,
            moder_role = False,
            writer_role = False,
            user_role = True
    )
   
    try:
        session = db.Session()
        session.add(user)
        session.commit()
    except:
        raise HTTPException(status_code = 409, detail = "Email or username already exists")

    return {"msg": "Successfully signup"}

@app.post("/users/login", status_code = 201)
def login(user_data: schemas.UserLogin, Authorize: AuthJWT = Depends()):
    password = user_data.password.encode("ascii", "strict")
    hash = None

    try:
        session = db.Session()
        hash = session.query(models.User.password_hash).filter_by(username = user_data.username).first().password_hash.encode("ascii", "strict")
        session.commit()
    except:
        raise HTTPException(status_code = 401, detail = "Bad credentials")

    if not bcrypt.checkpw(password, hash):
        raise HTTPException(status_code = 401, detail = "Bad credentials")

    access_token = Authorize.create_access_token(subject = user_data.username)
    refresh_token = Authorize.create_refresh_token(subject = user_data.username)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}

@app.post('/users/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    username = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject = username)
    Authorize.set_access_cookies(new_access_token)
    return {"access_token": new_access_token}

@app.delete('/users/logout', status_code = 200)
def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    return {"msg": "Successfully logout"}


