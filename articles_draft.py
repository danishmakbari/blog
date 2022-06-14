from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from main import app
from utils import *
import models
import schemas
import db

@app.post('/articles/draft/create', status_code = 201)
def create_draft(user_data: schemas.DraftCreate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    
    current_user_roles = get_user_roles(current_user)
    if not (current_user_roles["admin_role"] or current_user_roles["writer_role"]):
        raise HTTPException(status_code = 403, detail = "You need to be an admin or writer")
    
    draft = models.Article(
        header = user_data.header,
        body = user_data.body,
        state = "draft",
        decline_reason = ""
    )

    session = db.Session()
    session.add(draft)
    session.commit()

    author = models.ArticleAuthor(
        article_id = draft.id,
        author_id = get_userid_by_username(current_user),
        position = "creator"
    )

    session = db.Session()
    session.add(author)
    session.commit()

    return {"msg": "New draft was created"}

@app.post('/articles/draft/get', status_code = 201)
def get_draft(user_data: schemas.DraftGet, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    current_user_roles = get_user_roles(current_user)
    current_userid = get_userid_by_username(current_user) 

    session = db.Session()
    article = session.query(models.Article).filter_by(id = user_data.article_id).first()
    session.commit()   
    if not article or article.state != 'draft':
        raise HTTPException(status_code = 403, detail = "Article doesn't exist or article state is not draft")

    if current_user_roles["admin_role"] or current_user_roles["moder_role"]:
        return {"header": article.header, "body": article.body}
    elif current_user_roles["writer_role"]:
        session = db.Session()
        author = session.query(models.ArticleAuthor).filter((models.ArticleAuthor.article_id == user_data.article_id) & (models.ArticleAuthor.author_id == current_userid)).first()
        session.commit()

        if not author:
            raise HTTPException(status_code = 403, detail = "You need to be a creator, author or editor of the article")
        
        return {"header": article.header, "body": article.body}
    else:
        raise HTTPException(status_code = 403, detail = "You need to be an admin, moder or writer")

@app.put('/articles/draft/update', status_code = 200)
def update_draft(user_data: schemas.DraftUpdate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    current_user_roles = get_user_roles(current_user)
    current_userid = get_userid_by_username(current_user) 

    session = db.Session()
    article = session.query(models.Article).filter_by(id = user_data.article_id).first()
    session.commit()   
    if not article or article.state != 'draft':
        raise HTTPException(status_code = 403, detail = "Article doesn't exist or article state is not draft")

    if not (current_user_roles["admin_role"] or current_user_roles["writer_role"]):
        raise HTTPException(status_code = 403, detail = "You need to be an admin or writer")

    if current_user_roles["writer_role"]:
        session = db.Session()
        author = session.query(models.ArticleAuthor).filter((models.ArticleAuthor.article_id == user_data.article_id) & (models.ArticleAuthor.author_id == current_userid)).first()
        session.commit()
        if not author:
            raise HTTPException(status_code = 403, detail = "You need to be a creator, author or editor of the article")
         
    session = db.Session()
    session.query(models.Article).filter_by(id = user_data.article_id).update(
        {
            "header": user_data.header,
            "body": user_data.body,
        }
    )
    session.commit()

    return {"msg": "Draft was updated"}

@app.delete('/articles/draft/delete', status_code = 200)
def delete_draft(user_data: schemas.DraftDelete, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    current_user_roles = get_user_roles(current_user)
    current_userid = get_userid_by_username(current_user) 

    session = db.Session()
    article = session.query(models.Article).filter_by(id = user_data.article_id).first()
    session.commit()   
    if not article or article.state != 'draft':
        raise HTTPException(status_code = 403, detail = "Article doesn't exist or article state is not draft")

    if not (current_user_roles["admin_role"] or current_user_roles["writer_role"]):
        raise HTTPException(status_code = 403, detail = "You need to be an admin or writer")

    if current_user_roles["writer_role"]:
        session = db.Session()
        author = session.query(models.ArticleAuthor).filter((models.ArticleAuthor.article_id == user_data.article_id) & (models.ArticleAuthor.author_id == current_userid)).first()
        session.commit()
        if not author or author.position != "creator":
            raise HTTPException(status_code = 403, detail = "You need to be a creator of the article")

    session = db.Session()
    article = session.query(models.Article).filter_by(id = user_data.article_id).first()
    session.delete(article)
    session.commit()

    return {"msg": "Draft was deleted"}

@app.post('/articles/draft/move_to_published')
def move_to_published(user_data: schemas.DraftMoveToPublished, Authorize: AuthJWT = Depends()):
    return



