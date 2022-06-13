from pydantic import BaseModel, Field, EmailStr

class UserSignup(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdateRole(BaseModel):
    username: str
    rolename: str
    value: bool

class UserGetRoles(BaseModel):
    username: str

class UserCreateDraft(BaseModel):
    header: str
    body: str

class UserUpdateDraft(BaseModel):
    header: str
    body: str

