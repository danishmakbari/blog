from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from typing import Union

from main import app
from utils import *

import models
import schemas
import db

@app.post('/section', status_code = 201)
def f_section_post(data: schemas.SectionPost, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

    if not user_isadmin(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be an admin")

    section = models.ArticleSection(section = data.section)

    session = db.Session()
    session.add(section)
    session.commit()
  
    return {"section": data.section}

@app.get('/section', status_code = 200)
def f_section_post(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

    session = db.Session()
    sections = session.query(models.ArticleSection).all()
    session.commit()

    result = {"sections": []}
    for item in sections:
        result["sections"].append(item.section)

    return result

@app.get('/section/{section}', status_code = 200)
def f_section_article_get(section: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

    if not section_exists(section):
        raise HTTPException(status_code = 400, detail = "Section doesn't exist")

    session = db.Session()
    headers = session.query(
            models.Article.article_id,
            models.Article.header,
            models.Article.time_updated,
            models.Article.views,
            models.Article.avg_mark,
            models.Article.section
        ).filter((models.Article.state == "approved") & (models.Article.section == section)).order_by(models.Article.time_updated.desc()).all()
    session.commit()

    retval = {"headers": []}
    for item in headers:
        retval["headers"].append({
                    "article_id": item.article_id,
                    "header": item.header,
                    "time_updated": item.time_updated,
                    "views": item.views,
                    "avg_mark": item.avg_mark,
                    "section": item.section
                })

    return retval

@app.delete('/section', status_code = 200)
def f_section_post(data: schemas.SectionDelete, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

    if not user_isadmin(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be an admin")

    session = db.Session()
    section = session.query(models.ArticleSection).filter(models.ArticleSection.section == data.section).first()
    session.delete(section)
    session.commit()
  
    return {"section": data.section}


