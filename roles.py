from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from main import app
from utils import *
import models
import schemas
import db

@app.post("/users/roles/get", status_code = 201)
def get_roles(user_data: schemas.RolesGet, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    if not user_exists(user_data.username):
        raise HTTPException(status_code = 400, detail = "Wrong username")
    return get_user_roles(user_data.username)

@app.put('/users/roles/update', status_code = 200)
def update_roles(user_data: schemas.RolesUpdate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()

    current_user_roles = get_user_roles(current_user)
    if not current_user_roles["admin_role"]:
        raise HTTPException(status_code = 403, detail = "You need to be an admin")

    if not user_exists(user_data.username):
        raise HTTPException(status_code = 400, detail = "Wrong username")
    
    session = db.Session()
    session.query(models.User).filter_by(username = user_data.username).update(
        {
            "admin_role": user_data.admin_role,
            "moder_role": user_data.moder_role,
            "writer_role": user_data.writer_role,
            "user_role": user_data.user_role
        }
    )
    session.commit()
  
    return {"msg": "Roles were updated"}

