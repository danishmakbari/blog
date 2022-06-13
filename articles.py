from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from main import app
from utils import *
import models
import schemas
import db

@app.post('/articles/create_draft', status_code = 201)
def create_draft(user_data: schemas.UserCreateDraft, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    
    current_user_roles = get_user_roles(current_user)
    if not (current_user_roles["admin_role"] or current_user_roles["moder_role"] or current_user_roles["writer_role"]):
        raise HTTPException(status_code = 403, detail = "You need to be an admin, moder or writer")
    
    draft = models.Article(
        creator_id = get_userid_by_username(current_user),
        header = user_data.header,
        body = user_data.body,
        state = "draft",
        decline_reason = ""
    )
   
    session = db.Session()
    session.add(draft)
    session.commit()

    return {"msg": "New draft was created"}

@app.put('/articles/update_draft', status_code = 200)
def create_draft(user_data: schemas.UserUpdateDraft, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    
    current_user_roles = get_user_roles(current_user)
    if not (current_user_roles["admin_role"] or current_user_roles["moder_role"] or current_user_roles["writer_role"]):
        raise HTTPException(status_code = 403, detail = "You need to be an admin, moder or writer")


    return {"msg": "New draft was created"}


