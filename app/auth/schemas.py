
from pydantic import BaseModel, EmailStr # pydantic is for validation 

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"

class SigninRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class UserInfoResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
