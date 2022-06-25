from fastapi import HTTPException
import db
import models
import json

def section_exists(section: str):
    session = db.Session()
    section = session.query(models.ArticleSection).filter(models.ArticleSection.section == section).first()
    session.expunge_all() 
    session.commit()
    return section

def payload_check(payload: str):
    payload = json.loads(payload)
    user = user_get(payload["username"])
    if payload["temp_id"] != user.temp_id:
        raise HTTPException(status_code = 401, detail = "Unauthorized")
    return user.username

def user_exists(username: str):
    session = db.Session()
    user = session.query(models.User).filter(models.User.username == username).first()
    session.expunge_all() 
    session.commit()
    return user

def user_check_blacklist(username: str):
    user = user_get(username)
    if user.blacklist:
        raise HTTPException(status_code = 403, detail = "You are banned")
    return

def user_get(username: str):
    user = user_exists(username)
    if not user:
        raise HTTPException(status_code = 400, detail = "User doesn't exist")
    return user

def user_isadmin(username: str):
    return user_get(username).admin

def user_ismoder(username: str):
    return user_get(username).moder

def user_iswriter(username: str):
    return user_get(username).writer

def article_exists(article_id: int):
    session = db.Session()
    article = session.query(models.Article).filter(models.Article.article_id == article_id).first()
    session.expunge_all() 
    session.commit()
    return article

def article_get(article_id: int):
    article = article_exists(article_id)
    if not article:
        raise HTTPException(status_code = 400, detail = "Article doesn't exist")
    return article

def article_isdraft(article_id: int):
    return article_get(article_id).state == "draft"

def article_ispublished(article_id: int):
    return article_get(article_id).state == "published"

def article_isapproved(article_id: int):
    return article_get(article_id).state == "approved"

def article_isdeclined(article_id: int):
    return article_get(article_id).state == "declined"

def article_writers_get(article_id: int):
    session = db.Session()
    writers = session.query(models.ArticleWriter).filter(models.ArticleWriter.article_id == article_id).all()
    session.expunge_all() 
    session.commit()
    return [writer.username for writer in writers]

def article_iswriter(article_id: int, username: str):
    return username in article_writers_get(article_id)

def article_creator_get(article_id: int):
    session = db.Session()
    creator = session.query(models.ArticleWriter).filter((models.ArticleWriter.article_id == article_id) & (models.ArticleWriter.position == "creator")).first()
    session.expunge_all() 
    session.commit()
    return creator.username

def article_iscreator(article_id: int, username: str):
    return username == article_creator_get(article_id)

def article_authors_get(article_id: int):
    session = db.Session()
    authors = session.query(models.ArticleWriter).filter((models.ArticleWriter.article_id == article_id) & (models.ArticleWriter.position == "author")).all()
    session.expunge_all() 
    session.commit()
    return [author.username for author in authors]

def article_isauthor(article_id: int, username: str):
    return username in article_authors_get(article_id)

def article_editors_get(article_id: int):
    session = db.Session()
    editors = session.query(models.ArticleWriter).filter((models.ArticleWriter.article_id == article_id) & (models.ArticleWriter.position == "editor")).all()
    session.expunge_all() 
    session.commit()
    return [editor.username for editor in editors]

def article_iseditor(article_id: int, username: str):
    return username in article_editors_get(article_id)

def article_comments_get(article_id: int):
    session = db.Session()
    comments = session.query(models.Comment).filter(models.Comment.article_id == article_id).all()
    session.expunge_all() 
    session.commit()
    comments = [comment.__dict__ for comment in comments]
    for comment in comments:
        comment.pop("article_id")
    return comments




