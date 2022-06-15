from pydantic import BaseModel, EmailStr, validator

# Session
class SessionPost(BaseModel):
    username: str
    password: str

# User
class UserPost(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserUsernameRolesPut(BaseModel):
    admin: bool
    moder: bool
    writer: bool
    user: bool

# Draft
class DraftPost(BaseModel):
    header: str
    body: str

class DraftPut(BaseModel):
    header: str
    body: str

class DraftWriterPost(BaseModel):
    username: str
    position: str
    @validator("position")
    def check_position(cls, value):
        values = ["author", "editor"]
        if value not in values:
            raise ValueError("Invalid position")
        return value


class PublishedMoveToDeclined(BaseModel):
    article_id: int
    decline_reason: str

class PublishedMoveToApproved(BaseModel):
    article_id: int

