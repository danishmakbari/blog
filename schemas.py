from pydantic import BaseModel, Field, EmailStr

class UserSignup(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str



class RolesUpdate(BaseModel):
    username: str
    admin_role: bool
    moder_role: bool
    writer_role: bool
    user_role: bool

class RolesGet(BaseModel):
    username: str




class DraftCreate(BaseModel):
    header: str
    body: str

class DraftUpdate(BaseModel):
    article_id: int
    header: str
    body: str

class DraftGet(BaseModel):
    article_id: int

class DraftDelete(BaseModel):
    article_id: int

class DraftMoveToPublished(BaseModel):
    article_id: int









