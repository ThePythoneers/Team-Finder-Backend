from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


from auth import authentication
from database.models import (
    AllocationProposal,
    Custom_Roles,
    Department,
    Organization,
    TechnologyStack,
    User,
    Projects,
)
from database.db import SESSIONLOCAL
from project.base_models import (
    AddCustomRoleToProjectModel,
    AssignUserModel,
    CreateProjectModel,
    GetAvailableEmployeesModel,
    UpdateProjectModel,
)
from datetime import datetime, timedelta

router = APIRouter(prefix="/project", tags={"Projects"})


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


@router.post("/")
def create_project(db: DbDependency, user: UserDependency, _body: CreateProjectModel):
    """
    Functionality for Project Managers to create a new project.
    """
    action_user = db.query(User).filter_by(id=user["id"]).first()

    if "Project Manager" not in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Only a Project Manager can create a new project.",
        )

    if not _body.project_status in ["Not Started", "Starting"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="You can only assign Not Started and Starting when creating a new project.",
        )

    if _body.project_period == "Fixed" and not _body.deadline_date:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="If the project has a fixed project period, you must specify the deadline.",
        )
    elif _body.project_period != "Fixed" and _body.deadline_date:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="You cannot specify a deadline if the project period is not fixed.",
        )
    if _body.project_period == "Fixed":
        if (_body.deadline_date - _body.start_date).total_seconds() < 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="The deadline cannot be assigned before the start of the project.",
            )
    # if _body.work_hours <= 0 or _body.work_hours > 8:
    #     return JSONResponse(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         content="Work hours needs to be a value between 1 and 8",
    #     )
    create_project_model = Projects(
        project_name=_body.project_name,
        project_period=_body.project_period,
        project_status=_body.project_status,
        description=_body.general_description,
        start_date=_body.start_date,
        deadline_date=_body.deadline_date,
        # work_hours=_body.work_hours,
        organization_id=action_user.organization_id,
        project_manager=action_user.id,
    )
    for tech in _body.technologies:
        create_project_model.technologies.append(
            db.query(TechnologyStack).filter_by(id=tech).first()
        )
    for role in _body.team_roles:
        create_project_model.project_roles.append(
            db.query(Custom_Roles).filter_by(id=role).first()
        )
    create_project_model.users.append(action_user)

    db.add(create_project_model)
    db.commit()


@router.patch("/")
def update_project(db: DbDependency, user: UserDependency, _body: UpdateProjectModel):
    """
    Update an existing project, all fields are optional except project_id.
    """
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project_id = db.query(Projects).filter_by(id=_body.id).first()

    if "Project Manager" not in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=400, content="Only a Project Manager can update a new project."
        )

    if _body.project_period == "Fixed" and _body.project_period == "Ongoing":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Project period must be Fixed or Ongoing.",
        )

    if _body.project_period == "Fixed" and not _body.deadline_date:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="If the project has a fixed project period, you must specify the deadline.",
        )
    elif _body.project_period != "Fixed" and _body.deadline_date:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="You cannot specify a deadline if the project period is not fixed.",
        )

    if _body.deadline_date:
        if (_body.deadline_date - _body.start_date).total_seconds() < 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="The deadline cannot be assigned before the start of the project.",
            )

    # if _body.work_hours:
    #     if _body.work_hours < 0 or _body.work_hours > 8:
    #         return JSONResponse(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             content="Work hours needs to be a value between 1 and 8",
    #         )
    update_dict = {}

    project_id.project_name = _body.project_name
    project_id.project_period = _body.project_period
    project_id.start_date = _body.start_date
    project_id.deadline_date = _body.deadline_date
    project_id.project_status = _body.project_status
    project_id.description = _body.description
    project_id.work_hours = _body.work_hours

    db.commit()


@router.delete("/")
def delete_project(db: DbDependency, user: UserDependency, _id: UUID):
    """
    Functionality for Project Managers to delete a project.
    """
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(id=_id)

    if not project:
        return JSONResponse(status_code=400, content="This project does not exist.")
    if "Project Manager" not in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=400, content="Only a Project Manager can create a new project."
        )

    if not project.first():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This project has already been deleted or it does not exist.",
        )
    project.delete()
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK, content="Project deleted succesfully."
    )


@router.post("/assign")
def assign_user_to_project(
    db: DbDependency, user: UserDependency, _body: AssignUserModel
):
    project = db.query(Projects).filter_by(id=_body.project_id).first()
    victim_user = db.query(User).filter_by(id=_body.user_id).first()
    project.users.append(victim_user)
    victim_user.work_hours += project.work_hours
    db.commit()


@router.post("/find")
def get_available_employees(
    db: DbDependency, user: UserDependency, _body: GetAvailableEmployeesModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    organization = (
        db.query(Organization).filter_by(id=action_user.organization_id).first()
    )
    employees = organization.employees

    if not employees:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This organization does not have any employees.",
        )

    # ! TODO: check la technology si skills sa vedem daca se potrivesc

    available_employees = []

    for i in organization.employees:
        i.__dict__["method"] = []
        if _body.partially_available and i.work_hours < 8:
            i.__dict__["method"].append("partially_available")
            available_employees.append(i.__dict__)
        if _body.close_to_finish:
            for j in i.projects:
                project_deadline = j.deadline_date
                today = datetime.now().date()
                six_weeks_later = today + timedelta(weeks=6)

                if project_deadline:
                    if (
                        today
                        < project_deadline
                        < _body.deadline.date()
                        < six_weeks_later
                    ):

                        i.__dict__["method"].append("close_to_finish")
                        available_employees.append(i.__dict__)

        if _body.unavailable and i.work_hours >= 8:
            i.__dict__["method"].append("unavailable")
            available_employees.append(i.__dict__)
        if not i.projects:
            available_employees.append(i)
    return available_employees


@router.get("/{_id}")
def get_project_info(db: DbDependency, user: UserDependency, _id: str):
    project = db.query(Projects).filter_by(id=_id).first()
    project_dict = {
        "project_id": str(project.id),
        "project_name": project.project_name,
        "project_period": project.project_period,
        "start_date": str(project.start_date),
        "deadline_date": str(project.deadline_date),
        "project_status": project.project_status,
        "description": project.description,
        "users": [
            {"id": str(i.id), "username:": i.username, "email": i.email}
            for i in project.users
        ],
        "project_roles": [i.custom_role_name for i in project.project_roles],
        # "work_hours": project.work_hours,
        "technology_stack": [i.tech_name for i in project.technologies],
        "deallocated_users": [
            {"id": str(i.id), "username:": i.username}
            for i in project.deallocated_users
        ],
        "project_manager": str(project.project_manager),
    }

    return JSONResponse(status_code=200, content=project_dict)


@router.get("/all/")
def get_all_projects_info(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    projects = (
        db.query(Projects).filter_by(organization_id=action_user.organization_id).all()
    )
    if not projects:
        return []
    projects = action_user.projects

    if not projects:
        return []
    # if not projects:
    #     return JSONResponse(
    #         status_code=404, content="This organization does not have any projects yet."
    #     )
    project_list = []
    for i in projects:
        project_list.append(
            {
                "project_id": str(i.id),
                "project_name": i.project_name,
                "project_period": i.project_period,
                "start_date": str(i.start_date),
                "deadline_date": str(i.deadline_date) if i.deadline_date else None,
                "project_status": i.project_status,
                "description": i.description,
                "users": [
                    {"id": str(i.id), "username": i.username, "email": i.email}
                    for i in i.users
                ],
                "project_roles": [
                    {"id": str(i.id), "custom_role_name": i.custom_role_name}
                    for i in i.project_roles
                ],
                # "work_hours": i.work_hours,
                "technology_stack": [
                    {"id": str(i.id), "technology_name": i.tech_name}
                    for i in i.technologies
                ],
                "deallocated_users": [
                    {"id": str(j.id), "username:": j.username}
                    for j in i.deallocated_users
                ],
                "project_manager": str(i.project_manager),
            }
        )

    return JSONResponse(status_code=200, content=project_list)


@router.get("/user-info/{_id}")
def get_project_user_info(db: DbDependency, user: UserDependency, _id: str):
    users = {}
    project = db.query(Projects).filter_by(id=_id).first()
    proposed_to_project = (
        db.query(AllocationProposal).filter_by(project_id_allocation=_id).all()
    )
    users["proposed"] = [i.id for i in proposed_to_project]
    users["active"] = [i.id for i in project.users]
    users["deallocated"] = [i.id for i in project.deallocated_users]

    return users


@router.get("/info/department/{_id}")
def get_projects_related_to_department(
    db: DbDependency,
    user: UserDependency,
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = (
        db.query(Projects).filter_by(organization_id=action_user.organization_id).all()
    )
    related_projects = []
    for i in project:
        for j in i.users:
            if j.department_id == action_user.department_id:
                i.__dict__["evidentiated_user"] = str(j.id)
                related_projects.append(i)

    return_list = []
    for i in related_projects:
        return_list.append(
            {
                "evidentiated_user": i.evidentiated_user,
                "project_name": i.project_name,
                "deadline_date": i.deadline_date,
                "project_status": i.project_status,
                "users": [str(i.id) for i in i.users],
            }
        )
    # department = db.query(Department).filter_by(id=action_user.department_id).first()
    # projects = []
    # for i in department.department_users:
    #     print(i)
    #     projects.append(i.projects)

    # return_list = []

    # for j in projects:
    #     for j in i:
    #         return_list.append(
    #             {
    #                 "project_name": i.project_name,
    #                 "deadline_date": i.deadline_date,
    #                 "project_status": i.project_status,
    #                 "users": [str(i.id) for i in i.users],
    #             }
    #         )

    return return_list


@router.post("/roles")
def add_custom_role_to_project(
    db: DbDependency, user: UserDependency, _body: AddCustomRoleToProjectModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(project_manager=action_user.id).first()
    role_to_add = db.query(Custom_Roles).filter_by(id=_body.role_id).first()

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="You are not managing any projects.",
        )
    if not role_to_add:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="The role selected does not exist.",
        )
    if role_to_add in project.project_roles:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Cannot assign an already assigned role.",
        )
    project.project_roles.append(role_to_add)

    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content="Custom Role added succesfully."
    )


@router.delete("/roles")
def delete_custom_role_from_project(
    db: DbDependency, user: UserDependency, _body: AddCustomRoleToProjectModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(project_manager=action_user.id).first()
    role_to_delete = db.query(Custom_Roles).filter_by(id=_body.role_id).first()

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="You are not managing any projects.",
        )
    if not role_to_delete:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="The role selected does not exist.",
        )

    if not role_to_delete in project.project_roles:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Cannot find this role in this project.",
        )
    project.project_roles.remove(role_to_delete)

    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content="Custom Role deleted succesfully."
    )
