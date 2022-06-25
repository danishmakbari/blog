from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
import bcrypt
import random

from main import app
from utils import *

import models
import schemas
import db
import settings

# Signup
@app.post("/user", status_code = 201)
def f_user_post(data: schemas.UserPost):
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
            user = True,
            temp_id = random.randint(-32768, 32767)
    )
   
    try:
        session = db.Session()
        session.add(user)
        session.commit()
    except:
        raise HTTPException(status_code = 409, detail = "Email or username already exists")

    return {"username": data.username}

# Get info about current user
@app.get('/user/me', status_code = 200)
def f_user_me_get(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

    current_user = user_get(current_username)
 
    session = db.Session()
    draft = session.query(models.Article).join(models.ArticleWriter).filter((models.ArticleWriter.username == current_username) & (models.Article.state == "draft")).all()
    published = session.query(models.Article).join(models.ArticleWriter).filter((models.ArticleWriter.username == current_username) & (models.Article.state == "published")).all()
    approved = session.query(models.Article).join(models.ArticleWriter).filter((models.ArticleWriter.username == current_username) & (models.Article.state == "approved")).all()
    declined = session.query(models.Article).join(models.ArticleWriter).filter((models.ArticleWriter.username == current_username) & (models.Article.state == "declined")).all()
    session.commit()

    draft_arr = []
    published_arr = []
    approved_arr = []
    declined_arr = []
    for item in draft:
        draft_arr.append({
                    "article_id": item.article_id,
                    "header": item.header,
                    "time_updated": item.time_updated,
                    "views": item.views,
                    "avg_mark": item.avg_mark,
                    "section": item.section
            })
    for item in published:
        published_arr.append({
                    "article_id": item.article_id,
                    "header": item.header,
                    "time_updated": item.time_updated,
                    "views": item.views,
                    "avg_mark": item.avg_mark,
                    "section": item.section
            })
    for item in approved:
        approved_arr.append({
                    "article_id": item.article_id,
                    "header": item.header,
                    "time_updated": item.time_updated,
                    "views": item.views,
                    "avg_mark": item.avg_mark,
                    "section": item.section
            })
    for item in declined:
        declined_arr.append({
                    "article_id": item.article_id,
                    "header": item.header,
                    "time_updated": item.time_updated,
                    "views": item.views,
                    "avg_mark": item.avg_mark,
                    "section": item.section
            })

    return {
            "username": current_user.username,
            "email": current_user.email,
            "admin": current_user.admin,
            "moder": current_user.moder,
            "writer": current_user.writer,
            "user": current_user.user,
            "blacklist": current_user.blacklist,
            "draft": draft_arr,
            "published": published_arr,
            "approved": approved_arr,
            "declined": declined_arr
    }

# Get info about user
@app.get('/user/{username}', status_code = 200)
def f_user_get(username: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

    user = user_get(username)
 
    session = db.Session()
    approved = session.query(models.Article).join(models.ArticleWriter).filter((models.ArticleWriter.username == username) & (models.Article.state == "approved")).all()
    session.commit()

    approved_arr = []

    for item in approved:
        approved_arr.append({
                    "article_id": item.article_id,
                    "header": item.header,
                    "time_updated": item.time_updated,
                    "views": item.views,
                    "avg_mark": item.avg_mark,
                    "section": item.section
            })

    return {
            "username": user.username,
            "admin": user.admin,
            "moder": user.moder,
            "writer": user.writer,
            "user": user.user,
            "blacklist": user.blacklist,
            "approved": approved_arr
    }

# Update roles
@app.put('/user/{username}/role', status_code = 200)
def f_user_role_put(username: str, data: schemas.UserRolePut, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

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
  
    return {"username": username}

@app.put('/user/{username}/blacklist', status_code = 200)
def f_user_blacklist(username: str, data: schemas.UserBlackList, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

    if not user_isadmin(current_username):
        raise HTTPException(status_code = 403, detail = "Access denied")
 
    session = db.Session()
    session.query(models.User).filter(models.User.username == username).update({"blacklist": data.blacklist})
    session.commit()
  
    return {"username": username}
    

