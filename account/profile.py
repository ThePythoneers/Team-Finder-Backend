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
from database.models import Custom_Roles, User_Skills

from auth import authentication
from account.base_models import RoleRequestModel, SkillsRequestModel, DeleteSkillModel

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


@router.post("/skills")
def assign_skill_to_user(
    db: DbDependency, auth: UserDependency, _body: SkillsRequestModel
):
    """
    Users can assign themselves skills including their level and experience.
    """
    user = db.query(User).filter(id=auth["id"]).first()
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
    """
    Get all skills assigned to an user.
    """
    user = db.query(User).filter_by(id=auth["id"]).first()

    return user.skill_level


@router.delete("/skills")
def delete_skill_from_user(
    db: DbDependency, auth: UserDependency, _body: DeleteSkillModel
):
    """
    Delete a skill from an id.
    """
    user = db.query(User).filter_by(id=auth["id"]).first()
    if not "Department Manager" in [i.role_name for i in user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You need the Department Manager role to delete a skill.",
        )
    db.query(User_Skills).filter_by(
        user_id=_body.user_id, skill_id=_body.skill_id
    ).delete()
    db.commit()
