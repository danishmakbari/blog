from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
import bcrypt

from main import app
from utils import *

import models
import schemas
import db
import settings

# Signup
@app.post("/user", status_code = 201)
def user_post(data: schemas.UserPost):
    password = data.password.encode("ascii", "strict")
    hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode()
    
    user = models.User(
            email = data.email,
            username = data.username,
            password_hash = hash,
            blacklist = False,
            admin = False,
            moder = False,
            writer = False,
            user = True
    )
   
    try:
        session = db.Session()
        session.add(user)
        session.commit()
    except:
        raise HTTPException(status_code = 409, detail = "Email or username already exists")

    return {"msg": "Successfully signup"}

# Get info about current user
@app.get('/user/me', status_code = 200)
def user_me_get(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()

    current_user = user_get(current_username)

    return {
            "username": current_user.username,
            "email": current_user.email,
            "admin": current_user.admin,
            "moder": current_user.moder,
            "writer": current_user.writer,
            "user": current_user.user,
            "blacklist": current_user.blacklist
    }

# Get info about user
@app.get('/user/{username}', status_code = 200)
def fuser_get(username: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()

    if not user_exists(username):
        raise HTTPException(status_code = 400, detail = "Username doesn't exist")

    user = user_get(username)

    return {
            "username": user.username,
            "admin": user.admin,
            "moder": user.moder,
            "writer": user.writer,
            "user": user.user,
            "blacklist": user.blacklist
    }

# Update roles
@app.put('/user/{username}/roles', status_code = 200)
def user_roles_put(username: str, data: schemas.UserUsernameRolesPut, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()

    if not user_isadmin(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be an admin")

    if not user_exists(username):
        raise HTTPException(status_code = 400, detail = "Wrong username")
    
    session = db.Session()
    session.query(models.User).filter(models.User.username == username).update(
        {
            "admin": data.admin,
            "moder": data.moder,
            "writer": data.writer,
            "user": data.user
        }
    )
    session.commit()
  
    return {"msg": "Roles were updated"}


