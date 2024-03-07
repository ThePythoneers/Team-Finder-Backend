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
from database.models import Custom_Roles, Organization, User_Skills

from auth import authentication
from account.base_models import RoleRequestModel, SkillsRequestModel


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


@router.get("/get/{user}")
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


@router.post("/skills")
def assign_skill_to_user(
    db: DbDependency, auth: UserDependency, _body: SkillsRequestModel
):
    user = db.query(User).filter(User.id == auth["id"]).first()
    # 1 – Learns, 2 – Knows, 3 – Does, 4 – Helps, 5 – Teaches
    if not 1 < _body.level < 6:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Invalid skill level."
        )
    # 1 - 0-6 months, 2 - 6-12 months, 3 - 1-2 years
    # 4 - 2-4 years, 5 - 4-7 years, 6 - >7 years
    if not 1 < _body.experience < 7:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Invalid skill experience."
        )

    create_user_skills_model = User_Skills(
        user_id=user.id,
        skill_id=_body.skill_id,
        skill_level=_body.level,
        skill_experience=_body.experience,
    )

    db.add(create_user_skills_model)
    db.commit()


@router.get("/skills")
def get_skills_from_user(db: DbDependency, auth: UserDependency):
    user = db.query(User).filter(User.id == auth["id"]).first()

    return user.skill_level
