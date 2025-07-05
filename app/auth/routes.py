
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth import schemas, models, utils, dependencies
from app.utils import jwt
from app.core.database import get_db
import secrets
from typing import Dict

router = APIRouter() # starts new API router

# In-memory store for reset tokens
reset_tokens: Dict[str, int] = {}

# signup
@router.post("/signup")
def signup(data: schemas.SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        name=data.name,
        email=data.email,
        hashed_password=utils.hash_password(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Signup successful"}

#signin
@router.post("/signin", response_model=schemas.TokenResponse)
def signin(data: schemas.SigninRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not utils.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = jwt.create_access_token({"sub": str(user.id)})
    refresh_token = jwt.create_access_token({"sub": str(user.id)}, expires_delta=None)
    return schemas.TokenResponse(access_token=access_token, refresh_token=refresh_token)

# role
@router.get("/me", response_model=schemas.UserInfoResponse)
def get_my_info(current_user: models.User = Depends(dependencies.get_current_user)):
    return schemas.UserInfoResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role
    )

#forget password
@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    token = secrets.token_urlsafe(32)
    reset_tokens[token] = user.id

    # In production, send this token via email
    return {"message": "Reset token generated", "token": token}

#reset password
@router.post("/reset-password")
def reset_password(data: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    user_id = reset_tokens.pop(data.token, None)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = utils.hash_password(data.new_password)
    db.commit()

    return {"message": "Password reset successful"}
