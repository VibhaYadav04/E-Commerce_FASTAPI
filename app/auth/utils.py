
from passlib.context import CryptContext # for password hashing

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # use bcrypt algorithm for hashing password

# hash the password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# verify the password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
