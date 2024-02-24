from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from auth.models import OrganizationOwner, Token, Employee
from database.db import ENGINE, SESSIONLOCAL
from database import models
import string, random

router = APIRouter(prefix="/org")

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

@router.post("/{organization_link_ref}")
async def employee_registration(organization_link_ref: str, employee_register: Employee,  db: db_dependency):
    get_organization = db.query(models.Organizations).filter(models.Organizations.link_ref == organization_link_ref).first()

    create_employee_model = models.Employees(
        name = employee_register.username,
        email = employee_register.email,
        hashed_password = bcrypt_context.hash(employee_register.password)
    )

    db.add(create_employee_model)
    db.commit()
    
    return {"access" : get_organization.name}
    