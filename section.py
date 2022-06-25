from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

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

    try:
        session = db.Session()
        session.add(section)
        session.commit()
    except:
        raise HTTPException(status_code = 400, detail = "Already added")
  
    return {"section": data.section}

@app.get('/section', status_code = 201)
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

@app.delete('/section', status_code = 200)
def f_section_post(data: schemas.SectionDelete, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

    if not user_isadmin(current_username):
        raise HTTPException(status_code = 403, detail = "You need to be an admin")

    #try:
    session = db.Session()
    section = session.query(models.ArticleSection).filter(models.ArticleSection.section == data.section).first()
    session.delete(section)
    session.commit()
    #except:
    #    raise HTTPException(status_code = 400, detail = "Section doesn't exist")
  
    return {"section": data.section}


