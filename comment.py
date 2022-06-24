from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from main import app
from utils import *

import models
import schemas
import db

@app.delete('/comment/{comment_id}', status_code = 200)
def f_comment_delete(comment_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)
 
    if not user_ismoder(current_username):
        raise HTTPException(status_code = 403, detail = "Access denied")
    
    session = db.Session()
    comment = session.query(models.Comment).filter(models.Comment.comment_id == comment_id).first()
    session.delete(comment)
    session.commit()

    return {"comment_id": comment_id}

