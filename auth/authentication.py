"""
Auth module includes fancy registration and login for users and organization creation.
Home for token encryption and decryptions and user dependencies.
"""

import uuid

from datetime import timedelta, datetime
from typing import Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from dotenv import dotenv_values


from jose import jwt, JWTError

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from database.db import SESSIONLOCAL
from database import models

from auth.base_models import RegisterOwner, RegisterEmployee


from utils.utility import validate_email, validate_password, create_link_ref


router = APIRouter(tags={"Authentication"}, prefix="/auth")

env = dotenv_values(".env")

SECRET_KEY = env["SECRET_KEY"]
ALGORITHM = env["ALGORITHM"]
TOKEN_EXPIRATION_MINUTES = int(env["TOKEN_EXPIRATION_MINUTES"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    """
    creates a db session
    """
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()


DbDependency = Annotated[Session, Depends(get_db)]


@router.post("/employee/{linkref}")
def create_user_employee(
    db: DbDependency, create_user_request: RegisterEmployee, linkref: str
):
    """
    Register a user in an already existing organization a.k.a employee.
    """
    if not validate_email(create_user_request.email):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="invalid e-mail"
        )

    if not validate_password(create_user_request.password):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="invalid password"
        )

    if (
        db.query(models.User)
        .filter(models.User.email == create_user_request.email)
        .first()
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content="e-mail already exists"
        )

    create_user_model = models.User(
        id=uuid.uuid4(),
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )

    create_user_model.primary_roles.append(
        db.query(models.Primary_Roles).filter_by(role_name="Employee").first()
    )

    organization = db.query(models.Organization).filter_by(custom_link=linkref).first()
    organization.employees.append(create_user_model)
    db.add(create_user_model)
    db.add(organization)
    db.commit()


@router.post("/register/organization", status_code=status.HTTP_201_CREATED)
def create_user(db: DbDependency, create_user_request: RegisterOwner):
    """
    Register a user and an organization. The user will be an Organization Admin of the
    created organization.
    """
    if not validate_email(create_user_request.email):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="invalid e-mail"
        )

    if not validate_password(create_user_request.password):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="invalid password"
        )

    if (
        db.query(models.User)
        .filter(models.User.email == create_user_request.email)
        .first()
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content="e-mail already exists"
        )

    user_id = uuid.uuid4()

    create_user_model = models.User(
        id=user_id,
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    create_user_model.primary_roles.append(
        db.query(models.Primary_Roles).filter_by(role_name="Organization Admin").first()
    )
    create_organization_model = models.Organization(
        id=uuid.uuid4(),
        custom_link=create_link_ref(10),
        owner_id=user_id,
        organization_name=create_user_request.organization_name,
        hq_address=create_user_request.hq_address,
    )
    create_organization_model.employees.append(create_user_model)
    db.add(create_user_model)
    db.add(create_organization_model)
    db.commit()

    db.query(models.User).filter_by(id=create_user_model.id).first().organization_id = (
        create_organization_model.id
    )
    db.commit()

    return JSONResponse(status_code=201, content="Account created.")


@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDependency
):
    """
    Login as an user. Returns a time-limited token that can be used to
    get access to restricted endpoints.
    """
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Name or Password is incorrect.",
        )

    token = create_access_token(
        user.username, user.id, timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "uuid": str(user.id),
                "name": user.username,
                "email": user.email,
                "organization": str(user.organization_id),
                "organization_name": user.organization.organization_name,
                "roles": [i.role_name for i in user.primary_roles],
            },
        },
    )


@router.get("/token-info/{_token}")
def get_info_from_token(db: DbDependency, _token: str):
    _id = get_current_user(_token)["id"]
    user = db.query(models.User).filter_by(id=_id).first()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": _token,
            "token_type": "bearer",
            "user": {
                "uuid": str(user.id),
                "name": user.username,
                "email": user.email,
                "organization": str(user.organization_id),
                "organization_name": user.organization.organization_name,
                "roles": [i.role_name for i in user.primary_roles],
            },
        },
    )


def authenticate_user(email: str, password: str, db):
    """
    Verifies user password.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: str, expires_delta: timedelta):
    """
    Generates a token from the username and his uuid using JWT.
    """
    encode = {"sub": username, "id": str(user_id)}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """
    Dependency for restricting non-logged-in users from accessing endpoints that
    should not be visible to them.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"username": username, "id": user_id}
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        ) from exc
