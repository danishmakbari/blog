from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from main import app
from utils import *

import models
import schemas
import db

@app.post('/article', status_code = 201)
def f_article_post(data: schemas.ArticlePost, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)

    
    if not user_iswriter(current_username):
        raise HTTPException(status_code = 403, detail = "Access denied")
    
    article = models.Article(
        header = data.header,
        body = data.body,
        state = "draft",
        decline_reason = ""
    )

    session = db.Session()
    session.add(article)
    session.commit()

    creator = models.ArticleWriter(
        article_id = article.article_id,
        username = current_username,
        position = "creator"
    )

    session = db.Session()
    session.add(creator)
    session.commit()

    return {"article_id": article.article_id}

@app.get('/article/{article_id}', status_code = 200)
def f_article_get(article_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)
 
    if article_isdraft(article_id) or article_isdeclined(article_id):
        if not (user_iswriter(current_username) and article_iswriter(article_id, current_username)):
            raise HTTPException(status_code = 403, detail = "Access denied")
    elif article_ispublished(article_id):
        if not ((user_iswriter(current_username) and article_iswriter(article_id, current_username)) or user_ismoder(current_username)):
            raise HTTPException(status_code = 403, detail = "Access denied")
    
    return article_get(article_id).__dict__

@app.put('/article/{article_id}', status_code = 200)
def f_article_put(article_id: int, data: schemas.ArticlePut, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)

    if not (user_iswriter(current_username) and article_iswriter(article_id, current_username)):
        raise HTTPException(status_code = 403, detail = "Access denied")
 
    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")
    
    session = db.Session()
    session.query(models.Article).filter(models.Article.article_id == article_id).update(
        {
            "header": data.header,
            "body": data.body
        }
    )
    session.commit()

    return {"article_id": article_id}

@app.delete('/article/{article_id}', status_code = 200)
def f_article_delete(article_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)
 
    if not (user_iswriter(current_username) and article_iscreator(article_id, current_username)):
        raise HTTPException(status_code = 403, detail = "Access denied")

    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")
    
    session = db.Session()
    article = session.query(models.Article).filter(models.Article.article_id == article_id).first()
    session.delete(article)
    session.commit()

    return {"article_id": article_id}

@app.put('/article/{article_id}/state', status_code = 200)
def f_article_state_put(article_id: int, data: schemas.ArticleStatePut, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)

    if article_isdraft(article_id):
        if (not (user_iswriter(current_username) and article_iscreator(article_id, current_username))) or data.state != "published":
            raise HTTPException(status_code = 403, detail = "Access denied")
    
        session = db.Session()
        session.query(models.Article).filter(models.Article.article_id == article_id).update({"state": "published"})
        session.commit()
    
    elif article_ispublished(article_id):
        if user_ismoder(current_username):
            if data.state == "approved":
                session = db.Session()
                session.query(models.Article).filter(models.Article.article_id == article_id).update({"state": "approved", "decline_reason": ""})
                session.commit()
            elif data.state == "declined":
                session = db.Session()
                session.query(models.Article).filter(models.Article.article_id == article_id).update({"state": "declined", "decline_reason": data.decline_reason})
                session.commit()
            else:
                raise HTTPException(status_code = 403, detail = "Access denied")
        elif user_iswriter(current_username) and article_iscreator(article_id, current_username):
            if data.state != "draft":
                raise HTTPException(status_code = 403, detail = "Access denied")
            session = db.Session()
            session.query(models.Article).filter(models.Article.article_id == article_id).update({"state": "draft"})
            session.commit()
        else:
            raise HTTPException(status_code = 403, detail = "Access denied")

    else:
        if (not (user_iswriter(current_username) and article_iscreator(article_id, current_username))) or data.state != "draft":
            raise HTTPException(status_code = 403, detail = "Access denied")
    
        session = db.Session()
        session.query(models.Article).filter(models.Article.article_id == article_id).update({"state": "draft"})
        session.commit()
 
    return {"article_id": article_id}

@app.post('/article/{article_id}/writer')
def f_article_writer_post(article_id: int, data: schemas.ArticleWriterPost, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)
   
    if not (user_iswriter(current_username) and article_iscreator(article_id, current_username)):
        raise HTTPException(status_code = 403, detail = "Access denied")
 
    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")
    
    if article_iswriter(article_id, data.username):
        raise HTTPException(status_code = 400, detail = "Already added")

    writer = models.ArticleWriter(
        article_id = article_id,
        username = data.username,
        position = data.position
    )

    session = db.Session()
    session.add(writer)
    session.commit()

    return {"article_id": article_id}

@app.delete('/article/{article_id}/writer/{username}', status_code = 200)
def f_article_writer_delete(article_id: int, username: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)
    
    if not (user_iswriter(current_username) and article_iscreator(article_id, current_username)):
        raise HTTPException(status_code = 403, detail = "Access denied")
 
    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")
    
    if article_iscreator(article_id, username):
        raise HTTPException(status_code = 400, detail = "You are trying to delete a creator")

    session = db.Session()
    author = session.query(models.ArticleWriter).filter((models.ArticleWriter.article_id == article_id) & (models.ArticleWriter.username == username)).first()
    session.delete(author)
    session.commit()

    return {"article_id": article_id}

@app.get('/article/{article_id}/writer', status_code = 200)
def f_article_writer_get(article_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)
  
    if article_isdraft(article_id) or article_isdeclined(article_id):
        if not (user_iswriter(current_username) and article_iswriter(article_id, current_username)):
            raise HTTPException(status_code = 403, detail = "Access denied")
    elif article_ispublished(article_id):
        if not ((user_iswriter(current_username) and article_iswriter(article_id, current_username)) or user_ismoder(current_username)):
            raise HTTPException(status_code = 403, detail = "Access denied")

    return {
        "creator": article_creator_get(article_id),
        "authors": article_authors_get(article_id),
        "editors": article_editors_get(article_id)
    }

@app.get('/article/approved/header', status_code = 200)
def f_article_approved_get(first: int, last: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)

    session = db.Session()
    headers = session.query(models.Article.article_id, models.Article.header).filter(models.Article.state == "approved").all()
    session.commit()

    retval = {"headers": []}
    if first < len(headers):
        for i in range(first, min(last + 1, len(headers))):
            retval["headers"].append({"article_id": headers[i].article_id, "header": headers[i].header})

    return retval

@app.get('/article/published/header', status_code = 200)
def f_article_published_get(first: int, last: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)

    if not user_ismoder(current_username):
        raise HTTPException(status_code = 403, detail = "Access denied")

    session = db.Session()
    headers = session.query(models.Article.article_id, models.Article.header).filter(models.Article.state == "published").all()
    session.commit()

    retval = {"headers": []}
    if first < len(headers):
        for i in range(first, min(last + 1, len(headers))):
            retval["headers"].append({"article_id": headers[i].article_id, "header": headers[i].header})

    return retval

@app.get('/article/{article_id}/comment', status_code = 200)
def f_article_comment_get(article_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)
  
    if article_isdraft(article_id) or article_isdeclined(article_id):
        if not (user_iswriter(current_username) and article_iswriter(article_id, current_username)):
            raise HTTPException(status_code = 403, detail = "Access denied")
    elif article_ispublished(article_id):
        if not ((user_iswriter(current_username) and article_iswriter(article_id, current_username)) or user_ismoder(current_username)):
            raise HTTPException(status_code = 403, detail = "Access denied")

    return {"comments": article_comments_get(article_id)}

@app.post('/article/{article_id}/comment', status_code = 201)
def f_article_comment_post(article_id: int, data: schemas.ArticleCommentPost, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    user_check_blacklist(current_username)
    
    if not article_isapproved(article_id):
        raise HTTPException(status_code = 403, detail = "Access denied")

    comment = models.Comment(
        body = data.body,
        username = current_username,
        article_id = article_id
    )

    session = db.Session()
    session.add(comment)
    session.commit()

    return {"comment_id": comment.comment_id}

