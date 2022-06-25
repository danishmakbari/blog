from pydantic import BaseModel, EmailStr, validator
from typing import Union

# Session
class SessionPost(BaseModel):
    username: str
    password: str

# User
class UserPost(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserRolePut(BaseModel):
    admin: bool
    moder: bool
    writer: bool
    user: bool

class UserBlackList(BaseModel):
    blacklist: bool

# Article
class ArticlePost(BaseModel):
    header: str
    body: str
    section: Union[str, None]

class ArticlePut(BaseModel):
    header: str
    body: str
    section: Union[str, None]

class ArticleStatePut(BaseModel):
    state: str
    decline_reason: str
    @validator("state")
    def check_state(cls, value):
        values = ["draft", "published", "approved", "declined"]
        if value not in values:
            raise ValueError("Invalid state")
        return value


class ArticleWriterPost(BaseModel):
    username: str
    position: str
    @validator("position")
    def check_position(cls, value):
        values = ["author", "editor"]
        if value not in values:
            raise ValueError("Invalid position")
        return value

class ArticleCommentPost(BaseModel):
    body: str

class ArticleMarkPost(BaseModel):
    mark: int
    @validator("mark")
    def check_mark(cls, value):
        if value > 5 or value < 0:
            raise ValueError("Invalid mark")
        return value

class SectionPost(BaseModel):
    section: str

class SectionDelete(BaseModel):
    section: str

