from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserCreate(UserBase):
    openid: str


class UserUpdate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    openid: str
    points: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WeChatLoginRequest(BaseModel):
    code: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
