"""
Everythin related to an user's account. Like getting information about him,
assigning roles, assigning a department, etc.
"""

from typing import Annotated
from uuid import UUID


from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db import SESSIONLOCAL
from database.models import Projects, Skill, User, Skill_Category
from database.models import User_Skills

from auth import authentication
from account.base_models import SkillsRequestModel, DeleteSkillModel

router = APIRouter(tags={"User profile"}, prefix="/user")


def get_db():
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()


DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(authentication.get_current_user)]


@router.get("/get/{user_id}")
def get_user_info(db: DbDependency, auth: UserDependency, user_id: UUID):
    """
    Gets all user related info from an uuid.
    """
    # permission = ServerPermissions(db, auth)
    # if not permission.is_field_uuid(user):
    #     return JSONResponse(
    #         status_code=status.HTTP_400_NOT_FOUND,
    #         content="The uuid introduced is not valid.",
    #     )

    try:
        UUID(str(user_id), version=4)
    except:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="The UUID introduced is not valid.",
        )

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This account does not exist.",
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
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "organization_id": str(user.organization_id),
        "organization_name": user.organization.organization_name,
        "roles": [i.role_name for i in user.primary_roles],
        "department_id": (str(user.department_id) if user.department_id else None),
        "work_hours": user.work_hours,
    }
    return JSONResponse(content=user_data, status_code=status.HTTP_200_OK)


@router.post("/skills")
def assign_skill_to_user(
    db: DbDependency, auth: UserDependency, _body: SkillsRequestModel
):
    """
    Users can assign themselves skills including their level and experience.
    """
    action_user = db.query(User).filter_by(id=auth["id"]).first()
    # 1 – Learns, 2 – Knows, 3 – Does, 4 – Helps, 5 – Teaches
    if not 0 < _body.level < 6:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Invalid skill level."
        )
    # 1 - 0-6 months, 2 - 6-12 months, 3 - 1-2 years
    # 4 - 2-4 years, 5 - 4-7 years, 6 - >7 years
    if not 0 < _body.experience < 7:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="Invalid skill experience."
        )

    user_skill = (
        db.query(User_Skills)
        .filter_by(user_id=_body.user_id, skill_id=_body.skill_id)
        .first()
    )
    if user_skill:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You already have this skill equiped.",
        )

    create_user_skills_model = User_Skills(
        user_id=action_user.id,
        skill_id=_body.skill_id,
        skill_level=_body.level,
        skill_experience=_body.experience,
        training_title=_body.training_title,
        training_description=_body.training_description,
        project_link=_body.project_link,
    )

    # ! TODO: new column verified true / false (false by default)

    db.add(create_user_skills_model)
    db.commit()


@router.get("/skills")
def get_skills_from_user(db: DbDependency, auth: UserDependency):
    """
    Get all skills assigned to the logged-in user.
    """
    action_user = db.query(User).filter_by(id=auth["id"]).first()

    return_list = []

    for i in action_user.skill_level:
        skill = db.query(Skill).filter_by(id=i.skill_id).first()
        return_list.append(
            {
                "skill_id": str(i.skill_id),
                "skill_name": str(skill.skill_name),
                "skill_category": [str(i) for i in skill.skill_category],
                "skill_level": i.skill_level,
                "skill_experience": i.skill_experience,
                "training_title": str(i.training_title) if i.training_title else None,
                "training_description": (
                    str(i.training_description) if i.training_description else None
                ),
                "project_link": str(i.project_link) if i.project_link else None,
                "verified": i.verified,
            }
        )

    if not return_list:
        return JSONResponse(
            content="This user doesn't have any skills assigned",
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(content=return_list, status_code=status.HTTP_200_OK)


@router.get("/skills/any")
def get_skills_from_any_user(db: DbDependency, auth: UserDependency, _id: UUID):
    """
    Get all skills assigned to the logged-in user.
    """

    try:
        UUID(str(_id), version=4)
    except:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="The UUID introduced is not valid.",
        )

    victim_user = db.query(User).filter_by(id=_id).first()

    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_BAD_REQUEST, content="This user does not exist."
        )

    return_list = []
    for i in victim_user.skill_level:
        skill = db.query(Skill).filter_by(id=i.skill_id).first()
        return_list.append(
            {
                "skill_id": str(i.skill_id),
                "skill_name": str(skill.skill_name),
                "skill_category": [str(i) for i in skill.skill_category],
                "skill_level": i.skill_level,
                "skill_experience": i.skill_experience,
                "training_title": str(i.training_title) if i.training_title else None,
                "training_description": (
                    str(i.training_description) if i.training_description else None
                ),
                "project_link": str(i.project_link) if i.project_link else None,
            }
        )

    if not return_list:
        return JSONResponse(
            content="This user doesn't have any skills assigned",
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(content=return_list, status_code=status.HTTP_200_OK)


@router.delete("/skills")
def delete_skill_from_user(
    db: DbDependency, auth: UserDependency, _body: DeleteSkillModel
):
    """
    Delete a skill from an id.
    """

    skill = db.query(Skill).filter_by(id=_body.skill_id).first()

    if not skill:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="This Skill does not exist.",
        )

    user_skill = (
        db.query(User_Skills)
        .filter_by(user_id=_body.user_id, skill_id=_body.skill_id)
        .first()
    )

    if not user_skill:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="You cannot delete a skill that is not assigned to yourself.",
        )

    db.delete(user_skill)

    db.commit()


@router.get("/projects/{_id}")
def get_past_projects_info(db: DbDependency, user: UserDependency, _id: UUID):

    try:
        UUID(str(_id), version=4)
    except:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="The UUID introduced is not valid.",
        )

    action_user = db.query(User).filter_by(id=user["id"]).first()

    if not (
        "Project Manager" in [i.role_name for i in action_user.primary_roles]
        or "Employee" in [i.role_name for i in action_user.primary_roles]
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Project Managers and Employees are able to view past projects.",
        )

    projects = (
        db.query(Projects).filter_by(organization_id=action_user.organization_id).all()
    )
    project_list = []
    for i in projects:
        if action_user in i.users:
            _status = (
                "current"
                if i.project_status
                in ["Not Started", "Starting", "In Progress", "Closing"]
                else "past"
            )
            project_list.append(
                {
                    "project_name": i.project_name,
                    "project_roles": [
                        j.custom_role_name for j in i.project_roles
                    ],  # TODO
                    "technology_stack": i.technology_stack,
                    "status": _status,
                }
            )

    if not project_list:
        return JSONResponse(
            content="This user hasn't participated in any project yet.",
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(content=project_list, status_code=status.HTTP_200_OK)
