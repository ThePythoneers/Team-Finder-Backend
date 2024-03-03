"""
Everythin related to an user's account. Like getting information about him,
assigning roles, assigning a department, etc.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db import SESSIONLOCAL
from database.models import User
from database.models import Custom_Roles

from auth import authentication
from account.base_models import RoleRequestModel


router = APIRouter(tags={"User profile"}, prefix="/user")


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
UserDependency = Annotated[dict, Depends(authentication.get_current_user)]


@router.get("/{user}")
def get_user_info(db: DbDependency, auth: UserDependency, user: str):
    """
    Gets all user related info from an uuid.
    """
    user = db.query(User).filter(User.id == user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="This account does not exist."
        )

    if (
        db.query(User).filter_by(id=auth["id"]).first().organization_id
        != user.organization_id
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not allowed to view users from another organization other than yours.",
        )

    user_data = {
        "name": user.username,
        "email": user.email,
        "organization": user.organization.organization_name,
        "address": user.organization.hq_address,
        "primary_roles": user.primary_roles,
    }
    return user_data


@router.post("/customroles/add", status_code=status.HTTP_202_ACCEPTED)
def set_user_custom_role(
    db: DbDependency, auth: UserDependency, request: RoleRequestModel
):
    """
    Sets a custom role on the user.
    """
    role = db.query(Custom_Roles).filter_by(id=request.role_id).first()

    if (
        db.query(User).filter_by(id=auth["user_id"]).first().organization_id
        != db.query(User).filter_by(id=request.user_id).first().organization_id
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not allowed to view users from another organization other than yours.",
        )
    if not role:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="This role does not exist."
        )

    role.employees.append(db.query(User).filter_by(id=request.user_id).first())

    db.commit()
