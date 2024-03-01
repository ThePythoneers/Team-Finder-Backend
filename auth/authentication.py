from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from auth.models import RegisterOwner, RegisterEmployee, Token
from database.db import ENGINE, SESSIONLOCAL
from database import models
import string, random, uuid


router = APIRouter(
    tags={"Authentication"},
    prefix="/auth"
    )

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

@router.post("/employee/{linkref}", status_code=status.HTTP_201_CREATED)
async def create_user_employee(db:db_dependency, create_user_request: RegisterEmployee, linkref: str):
    if db.query(models.User).filter(models.User.email == create_user_request.email).first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"There is already an account created with this email")
       
    user_id = uuid.uuid4()
    create_user_model = models.User(
        id = user_id,
        username = create_user_request.username,
        email = create_user_request.email,
        hashed_password = bcrypt_context.hash(create_user_request.password),
    )
    organization = db.query(models.Organization).filter_by(custom_link = linkref).first()
    organization.employees.append(create_user_model)
    db.add(create_user_model)
    db.add(organization)
    db.commit()


@router.post("/register/organization", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: RegisterOwner):   
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    create_user_model = models.User(
        id = user_id,
        username = create_user_request.username,
        email = create_user_request.email,
        hashed_password = bcrypt_context.hash(create_user_request.password),
    )
    
    if not db.query(models.User).filter(models.User.email == create_user_model.email).first():
        db.add(create_user_model)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"There is already an account created with this email")
    
    create_organization_model = models.Organization(
        id = organization_id,
        custom_link = create_link_ref(10),
        owner_id = user_id,
        organization_name = create_user_request.organization_name,
        hq_address = create_user_request.hq_address,
    )
    create_organization_model.employees.append(create_user_model)
    db.add(create_organization_model)
    db.commit()

    db.query(models.User).filter_by(id = create_user_model.id).first().organization_id = create_organization_model.id
    db.commit()



def create_link_ref(length: int, chars = string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for i in range(length))


@router.post("/token")
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Name or Password is incorrect.")

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "uuid": user.id,
            "name": user.username,
            "email": user.email
        }  
    }

def authenticate_user(email: str, password: str, db):
    user = db.query(models.User).filter(models.User.email == email).first()
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
