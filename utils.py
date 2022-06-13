import db
import models

def user_exists(username_var: str):
    session = db.Session()
    ret = bool(session.query(models.User).filter_by(username = username_var).first())
    session.commit()
    return ret

def get_user_roles(username_var: str):
    session = db.Session()
    user = session.query(models.User).filter_by(username = username_var).first()
    session.commit()
    return {
        "admin_role": user.admin_role,
        "moder_role": user.moder_role,
        "writer_role": user.writer_role,
        "user_role": user.user_role
    }

def get_userid_by_username(username_var: str):
    session = db.Session()
    userid = session.query(models.User).filter_by(username = username_var).first().id
    session.commit()
    return userid

