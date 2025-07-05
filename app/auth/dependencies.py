from fastapi import Depends, HTTPException, status 
# Depends: Used for dependency injection ...HTTPException: Allows returning a proper HTTP error....status: Contains standard HTTP status codes.
from fastapi.security import OAuth2PasswordBearer # getting jwt token
from sqlalchemy.orm import Session # used to interact with database
from jose import JWTError
from app.auth.models import User
from app.core.database import get_db
from app.utils.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin") # extract token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User: # extract user
    try: # decode token
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError): # if fail then unauthorised error
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# check user id matched or not
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# check if admin
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

