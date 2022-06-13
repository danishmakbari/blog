from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from main import app
from utils import *
import models
import schemas
import db

def check_rolename(rolename: str):
    roles = ["admin_role", "moder_role", "writer_role", "user_role"]
    return rolename in roles

@app.post("/users/get_roles", status_code = 201)
def get_roles(user_data: schemas.UserGetRoles, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return get_user_roles(user_data.username)

@app.put('/users/update_role', status_code = 200)
def update_role(user_data: schemas.UserUpdateRole, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()

    current_user_roles = get_user_roles(current_user)
    if not current_user_roles["admin_role"]:
        raise HTTPException(status_code = 403, detail = "You need to be an admin")

    if not user_exists(user_data.username) or not check_rolename(user_data.rolename):
        raise HTTPException(status_code = 400, detail = "Wrong username or rolename")
    
    session = db.Session()
    session.query(models.User).filter_by(username = user_data.username).update({user_data.rolename: user_data.value})
    session.commit()
  
    return {"msg": "Role was updated"}

