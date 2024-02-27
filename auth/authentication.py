from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from auth.models import Users, Token
from database.db import ENGINE, SESSIONLOCAL
from database import models
import string, random

router = APIRouter(prefix="/auth")

SECRET_KEY = "1CD6923F4C8F1B56A775FDF2C0F95C51601F43DBD6376A11954786242F76FFFC28017BAA0457939D04F558AA6F0D09EE92076FD1CC6CBB39F8E4B8C2F2FE5500"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: Users):
    if not create_user_request.type_ in ["employee", "owner"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed request: This type of account does not exist.")
    
    create_user_model = models.Users(
        username = create_user_request.username,
        type_ = create_user_request.type_,
        email = create_user_request.email,
        organization_name = create_user_request.organization_name,
        hq_address = create_user_request.hq_address,
        hashed_password = bcrypt_context.hash(create_user_request.password)
    )

    if not db.query(models.Users).filter(models.Users.email == create_user_model.email).first():
        db.add(create_user_model)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"There is already an account created with this email")
    
    if create_user_request.type_ == "owner":
        create_organization_model = models.Organizations(
            link_ref = create_link_ref(10),
            name = create_user_model.organization_name,
            owner = create_user_model.uuid
        )
        db.add(create_organization_model)
        db.commit()

def create_link_ref(length: int, chars = string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for i in range(length))


@router.post("/token")
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Name or Password is incorrect.")

    token = create_access_token(user.username, user.uuid, timedelta(minutes=20))
    return {
        "access_token": token,
        "token_type": "bearer",
        user: {
            "uuid": user.uuid,
            "name": user.username,
            "email": user.email
        }  
    }

def authenticate_user(email: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: str, expires_delta: timedelta):
    encode = {"sub": username, "id": str(user_id)}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
            return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail = "JWTERROR, WTF?")
