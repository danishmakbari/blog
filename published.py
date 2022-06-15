from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from main import app
from utils import *

import models
import schemas
import db

@app.get('/published/get_all', status_code = 200)
def published_get_all(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()

    if not user_ismoder(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a moder")

    session = db.Session()
    articles = session.query(models.Article).filter(models.Article.state == "published").all()
    session.commit()

    retval = {"articles": []}
    for article in articles:
        retval["articles"].append({"article_id": article.article_id, "header": article.header, "body": article.body})

    return retval

@app.put('/published/move_to_approved', status_code = 200)
def published_move_to_approved(data: schemas.PublishedMoveToApproved, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()

    if not article_exists(data.article_id):
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")

    if not article_ispublished(data.article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not published")

    if not user_ismoder(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a moder")

    session = db.Session()
    session.query(models.Article).filter(models.Article.article_id == data.article_id).update({"state": "approved"})
    session.commit()

    return {"msg": "Article was approved"}



@app.put('/published/move_to_declined', status_code = 200)
def published_move_to_declined(data: schemas.PublishedMoveToDeclined, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()

    if not article_exists(data.article_id):
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")

    if not article_ispublished(data.article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not published")

    if not user_ismoder(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a moder")

    session = db.Session()
    session.query(models.Article).filter(models.Article.article_id == data.article_id).update({"state": "declined", "decline_reason": data.decline_reason})
    session.commit()

    return {"msg": "Article was declined"}



