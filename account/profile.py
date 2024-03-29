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
from database.models import (
    Notifications,
    Projects,
    Skill,
    User,
    Skill_Category,
    WorkHours,
)
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

    work_hours = db.query(WorkHours).filter_by(user_id=user_id).all()
    total_work_hours = 0
    for work in work_hours:
        total_work_hours += work.work_hours

    user_data = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "organization_id": str(user.organization_id),
        "organization_name": user.organization.organization_name,
        "roles": [i.role_name for i in user.primary_roles],
        "department_id": (str(user.department_id) if user.department_id else None),
        "projects": [str(i.id) for i in user.projects],
        "work_hours": total_work_hours,
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
        .filter_by(user_id=action_user.id, skill_id=_body.skill_id)
        .first()
    )
    if user_skill:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You already have this skill equiped.",
        )
    if _body.project_link:
        project = db.query(Projects).filter_by(id=_body.project_link).first()
        if not project:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="The project linked to project_link does not exist.",
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

    if action_user.department:
        if action_user.department.department_manager:
            notification = Notifications(
                type="VALIDATION",
                to_manager=action_user.department.department_manager,
                for_user=action_user.id,
            )
            db.add(notification)
    db.add(create_user_skills_model)
    db.commit()


@router.get("/skills/project-link/{_id}")
def get_project_link_info(db: DbDependency, user: UserDependency, _id: UUID):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    user_skill = (
        db.query(User_Skills).filter_by(user_id=action_user.id, skill_id=_id).first()
    )
    if not user_skill.project_link:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="This skill does not have a project link",
        )
    project = db.query(Projects).filter_by(id=user_skill.project_link).first()

    if project.organization_id != action_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content="You are not allowed to view projects from another organization",
        )

    project_dict = {
        "project_id": str(project.id),
        "project_name": project.project_name,
        "project_period": project.project_period,
        "start_date": str(project.start_date),
        "deadline_date": str(project.deadline_date),
        "project_status": project.project_status,
        "description": project.description,
        "users": [{"id": str(i.id), "username:": i.username} for i in project.users],
        "project_roles": [
            {"id": str(i.id), "role_name": i.custom_role_name}
            for i in project.project_roles
        ],
        "technology_stack": [i.tech_name for i in project.technologies],
        "deallocated_users": [
            {"id": str(i.id), "username:": i.username}
            for i in project.deallocated_users
        ],
        "project_manager": str(project.project_manager),
    }
    return project_dict


@router.patch("/skills")
def edit_skill_from_user(
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
        .filter_by(user_id=action_user.id, skill_id=_body.skill_id)
        .first()
    )
    if not user_skill:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This skill does not exist.",
        )

    user_skill.verified = False
    user_skill.skill_level = _body.level
    user_skill.skill_experience = _body.experience
    user_skill.training_title = _body.training_title
    user_skill.training_description = _body.training_description
    user_skill.project_link = _body.project_link

    # ! TODO: new column verified true / false (false by default)
    if action_user.department:
        if action_user.department.department_manager:
            notification = Notifications(
                type="VALIDATION",
                to_manager=action_user.department.department_manager,
                for_user=action_user.id,
            )
            db.add(notification)

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
                "verified": i.verified,
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
    action_user = db.query(User).filter_by(id=auth["id"]).first()
    skill = db.query(Skill).filter_by(id=_body.skill_id).first()

    if not skill:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="This Skill does not exist.",
        )

    user_skill = (
        db.query(User_Skills)
        .filter_by(user_id=action_user.id, skill_id=_body.skill_id)
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
