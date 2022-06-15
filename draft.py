from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from main import app
from utils import *

import models
import schemas
import db

@app.post('/draft', status_code = 201)
def draft_post(data: schemas.DraftPost, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    
    if not user_iswriter(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a writer")
    
    draft = models.Article(
        header = data.header,
        body = data.body,
        state = "draft",
        decline_reason = ""
    )

    session = db.Session()
    session.add(draft)
    session.commit()

    writer = models.ArticleWriter(
        article_id = draft.article_id,
        username = current_username,
        position = "creator"
    )

    session = db.Session()
    session.add(writer)
    session.commit()

    return {"article_id": draft.article_id}

@app.get('/draft/{article_id}', status_code = 200)
def draft_get(article_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
  
    if not article_exists(article_id):
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")

    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")

    if not user_iswriter(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a writer")
 
    if not article_iswriter(article_id, current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a creator, author or editor of the article")
  
    article = article_get(article_id)

    return {"header": article.header, "body": article.body}

@app.put('/draft/{article_id}', status_code = 200)
def draft_put(article_id: int, data: schemas.DraftPut, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()

    if not article_exists(article_id):
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")

    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")

    if not user_iswriter(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a writer")
 
    if not article_iswriter(article_id, current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a creator, author or editor of the article")
        
    session = db.Session()
    session.query(models.Article).filter(models.Article.article_id == article_id).update(
        {
            "header": data.header,
            "body": data.body
        }
    )
    session.commit()

    return {"msg": "Draft was updated"}

@app.delete('/draft/{article_id}', status_code = 200)
def draft_delete(article_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
 
    if not article_exists(article_id):
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")

    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")

    if not user_iswriter(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a writer")
 
    if not article_iscreator(article_id, current_username):   
        raise HTTPException(status_code = 403, detail = "You need to be a creator of the article")

    session = db.Session()
    article = session.query(models.Article).filter(models.Article.article_id == article_id).first()
    session.delete(article)
    session.commit()

    return {"msg": "Draft was deleted"}

@app.put('/draft/{article_id}/topublished', status_code = 200)
def draft_topublished_put(article_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
  
    if not article_exists(article_id):
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")

    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")

    if not user_iswriter(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a writer")
 
    if not article_iscreator(article_id, current_username):   
        raise HTTPException(status_code = 403, detail = "You need to be a creator of the article")

    session = db.Session()
    session.query(models.Article).filter(models.Article.article_id == article_id).update({"state": "published"})
    session.commit()

    return {"msg": "Draft was moved to published"}

@app.post('/draft/{article_id}/writer')
def draft_wirter_post(article_id: int, data: schemas.DraftWriterPost, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
   
    if not article_exists(article_id):
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")

    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")

    if not user_iswriter(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a writer")
 
    if not article_iscreator(article_id, current_username):   
        raise HTTPException(status_code = 403, detail = "You need to be a creator of the article")

    if not user_exists(data.username):
        raise HTTPException(status_code = 400, detail = "User doesn't exist")

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

    return {"msg": "New writer was added"}

@app.delete('/draft/{article_id}/writer/{username}', status_code = 200)
def draft_writer_delete(article_id: int, username: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
    
    if not article_exists(article_id):
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")

    if not article_isdraft(article_id):
        raise HTTPException(status_code = 400, detail = "Article state is not draft")

    if not user_iswriter(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be a writer")
 
    if not article_iscreator(article_id, current_username):   
        raise HTTPException(status_code = 403, detail = "You need to be a creator of the article")

    if not user_exists(username):
        raise HTTPException(status_code = 400, detail = "User doesn't exist")

    if article_iscreator(article_id, username):
        raise HTTPException(status_code = 400, detail = "You are trying to delete a creator")

    session = db.Session()
    author = session.query(models.ArticleWriter).filter((models.ArticleWriter.article_id == article_id) & (models.ArticleWriter.username == username)).first()
    session.delete(author)
    session.commit()

    return {"msg": "Article writer was removed"}

@app.get('/draft/{article_id}/writer', status_code = 200)
def draft_writer_get(article_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = Authorize.get_jwt_subject()
   
    if not article_exists(article_id):
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")
    
    return {
        "creator": article_creator_get(article_id),
        "authors": article_authors_get(article_id),
        "editors": article_editors_get(article_id)
    }





