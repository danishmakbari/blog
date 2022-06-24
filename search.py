from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from main import app
from utils import *

import models
import schemas
import db

@app.get('/search', status_code = 200)
def f_search_get(search_string: str, sort_type: str, order: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_username = payload_check(Authorize.get_jwt_subject())
    user_check_blacklist(current_username)

    search_string = search_string.split()
    for i in range(len(search_string)):
        search_string[i] = '%' + search_string[i] + '%'
    like =  (models.Article.header.ilike(search_string[0])) | (models.Article.body.ilike(search_string[0])) | (models.ArticleWriter.username.ilike(search_string[0]))
    for i in range(1, len(search_string)):
        like = (like) & ((models.Article.header.ilike(search_string[i])) | (models.Article.body.ilike(search_string[i])) | (models.ArticleWriter.username.ilike(search_string[i])))


    #search_string = '%' + search_string + '%'

    session = db.Session()

    values = session.query(
            models.Article.article_id,
            models.Article.header,
            models.Article.views,
            models.Article.avg_mark,
            models.Article.time_updated,
            models.ArticleWriter.username
        ).filter(
            (models.Article.state == "approved") & (
                like
                #(models.Article.header.ilike(search_string)) |
                #(models.Article.body.ilike(search_string)) |
                #(models.ArticleWriter.username.ilike(search_string))
            )
        )

    field = None
    if sort_type == "date":
        field = models.Article.time_updated
    elif sort_type == "avg_mark":
        field = models.Article.avg_mark
    elif sort_type == "views":
        field = models.Article.views
    else:
        raise HTTPException(status_code = 400, detail = "Wrong sort type")

    if order == "asc":
        field = field.asc()
    elif order == "desc":
        field = field.desc()
    else:
        raise HTTPException(status_code = 400, detail = "Wrong order")

    values = values.order_by(field).all()

    session.commit()

    ids = [item.article_id for item in values]
    result = []
    result_ids = []
    
    for i in range(len(ids)):
        if ids[i] not in result_ids:
            result_ids.append(ids[i])
            result.append({
                "article_id": values[i].article_id, 
                "header": values[i].header,
                "views": values[i].views, 
                "avg_mark": values[i].avg_mark,
                "date": values[i].time_updated
            })

    return {"headers": result}

