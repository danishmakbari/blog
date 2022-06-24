from fastapi import HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
import bcrypt
from starlette.responses import RedirectResponse
import requests
import random
import json

from main import app
from utils import *

import schemas
import db
import settings

class Settings(BaseModel):
    authjwt_secret_key: str = settings.jwt["secret"]
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

    user = user_get(data.username)
    hash = user.password_hash.encode("ascii", "strict")
    password = data.password.encode("ascii", "strict")
    
    if not bcrypt.checkpw(password, hash):
        raise HTTPException(status_code = 401, detail = "Bad credentials")

    payload = json.dumps({"username": user.username, "temp_id": user.temp_id})
    access_token = Authorize.create_access_token(subject = payload)
    refresh_token = Authorize.create_refresh_token(subject = payload)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}

# Refresh access token
@app.put('/session', status_code = 200)
def f_session_put(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user = user_get(current_username)
    payload = json.dumps({"username": user.username, "temp_id": user.temp_id})
    new_access_token = Authorize.create_access_token(subject = payload)
    Authorize.set_access_cookies(new_access_token)
    return {"access_token": new_access_token}

# Logout
@app.delete('/session', status_code = 200)
def f_session_delete(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    Authorize.unset_jwt_cookies()
    return {"msg": "Successfully logout"}

@app.put('/session/all', status_code = 200)
def f_session_all_put(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    session = db.Session()
    user = session.query(models.User).filter(models.User.username == current_username).first()
    randval = user.temp_id
    while randval == user.temp_id:
        randval = random.randint(-32768, 32767)
    session.query(models.User).filter(models.User.username == current_username).update({"temp_id": randval})
    session.commit()

    payload = json.dumps({"username": user.username, "temp_id": user.temp_id})
    access_token = Authorize.create_access_token(subject = payload)
    refresh_token = Authorize.create_refresh_token(subject = payload)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}



@app.get("/session/mailru", status_code = 200)
def f_session_mailru_get(request: Request):
    url = "https://o2.mail.ru/login?client_id={}&response_type={}&scope={}&redirect_uri={}&state={}".format(
            settings.mailru["id"],
            "code",
            "biz.api%20userinfo",
            "https://{}:{}/session/mailru/callback".format(settings.web_server["host"], settings.web_server["port"]),
            "state"
    )
    return RedirectResponse(url = url)

@app.get("/session/mailru/callback", status_code = 200)
def f_session_mailru_callback_get(state: str, code: str, Authorize: AuthJWT = Depends()):
    url = "https://o2.mail.ru/token?grant_type={}&code={}&redirect_uri={}".format(
            "authorization_code",
            code,
            "https://{}:{}/session/mailru/callback".format(settings.web_server["host"], settings.web_server["port"])
    )
    response = requests.post(url, auth = requests.auth.HTTPBasicAuth(settings.mailru["id"], settings.mailru["secret"]))
    access_token = response.json()["access_token"]
   
    url = "https://o2.mail.ru/userinfo?access_token={}".format(access_token)
    response = requests.get(url)
    data = response.json()

    user = models.User(
            email = data["email"],
            username = data["email"],
            password_hash = None,
            blacklist = False,
            admin = False,
            moder = False,
            writer = False,
            user = True,
            temp_id = random.randint(-32768, 32767)
    )
   
    try:
        session = db.Session()
        session.add(user)
        session.commit()
    except:
        pass

    user = user_get(user.username)

    payload = json.dumps({"username": user.username, "temp_id": user.temp_id})
    access_token = Authorize.create_access_token(subject = payload)
    refresh_token = Authorize.create_refresh_token(subject = payload)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}

