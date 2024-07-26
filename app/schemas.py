from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

'''
Base classes have the common attributes for both reading and creating
'''

class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserCredentials(BaseModel):
    email: EmailStr
    password: str


class UserPasswordChangeSchema(UserCredentials):
    new_password: str


class SuperUserCredentials(UserCredentials):
    superuser_password: str


class User(BaseModel):
    user_id: int
    email: EmailStr

    class Config:
        orm_mode = True


class UserInfo(User):
    fullname: Optional[str] = None
    designation: Optional[str] = None
    staff_id: Optional[int] = None

    class Config:
        orm_mode = True


class UserInfoCreate(BaseModel):
    fullname: str
    designation: str
    staff_id: int

    class Config:
        orm_mode = True


class RegistrationWithInfoSchema(BaseModel):
    email: EmailStr
    password: str
    fullname: str
    designation: str
    staff_id: int


# ===============Token Schemas================
class AccessToken(BaseModel):
    access_token: str


# ==============JWT Payload Schemas==========
class AccessTokenPayloadBase(BaseModel):
    sub: int
    role: str
    session_id: str
    token_type: str = 'access'

class AccessTokenInputData(AccessTokenPayloadBase):
    pass

class AccessTokenPayload(AccessTokenPayloadBase):
    exp: datetime | Any