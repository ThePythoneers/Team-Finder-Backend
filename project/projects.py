from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


from auth import authentication
from database.models import Organization, User, Projects
from database.db import SESSIONLOCAL
from project.base_models import (
    AssignUserModel,
    CreateProjectModel,
    GetAvailableEmployeesModel,
    UpdateProjectModel,
)
from datetime import date, timedelta

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
            status_code=400, content="Only a Project Manager can create a new project."
        )

    if not _body.project_period == "Fixed" and _body.deadline_date is not None:
        return JSONResponse(status_code=400, content="Bad project period.")

    if _body.project_status not in ["Not Started", "Starting"]:
        return JSONResponse(
            status_code=400,
            content="You can only assign Not Started and \
                             Starting when creating a new project.",
        )

    create_project_model = Projects(
        project_name=_body.project_name,
        project_period=_body.project_period,
        project_status=_body.project_status,
        description=_body.general_description,
        start_date=_body.start_date,
        deadline_date=_body.deadline_date,
        technology_stack=_body.technology_stack,
    )
    print("test")
    # TODO create_project_model.project_roles.append(_body.team_roles)

    db.add(create_project_model)
    db.commit()


@router.patch("/")
def update_project(db: DbDependency, user: UserDependency, _body: UpdateProjectModel):
    """
    Update an existing project, all fields are optional except project_id.
    """
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project_id = db.query(Projects).filter_by(id=_body.project_id)

    if "Project Manager" not in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=400, content="Only a Project Manager can update a new project."
        )
    if _body.project_status and _body.project_status not in ["Not Started", "Starting"]:
        return JSONResponse(
            status_code=400,
            content="You can only assign Not Started and \
                             Starting when creating a new project.",
        )

    update_dict = {}

    if _body.project_name:
        update_dict["project_name"] = _body.project_name
    if _body.project_period:
        update_dict["project_period"] = _body.project_period
    if _body.start_date:
        update_dict["start_date"] = _body.start_date
    if _body.deadline_date:
        update_dict["deadline_date"] = _body.deadline_date
    if _body.project_status:
        update_dict["project_status"] = _body.project_status
    if _body.general_description:
        update_dict["general_description"] = _body.general_description
    if _body.technology_stack:
        update_dict["technology_stack"] = _body.technology_stack
    # TODO if _body.team_roles:
    # TODO    update_dict["team_roles"] = _body.team_roles

    print(_body)
    project_id.update(update_dict)

    db.commit()


@router.delete("/")
def delete_project(db: DbDependency, user: UserDependency, _id: UUID):
    """
    Functionality for Project Managers to delete a project.
    """
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(id=_id)

    if "Project Manager" not in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=400, content="Only a Project Manager can create a new project."
        )

    # TODO create_project_model.project_roles.append(_body.team_roles)

    project.delete()
    db.commit()


@router.post("/assign")
def assign_user_to_project(
    db: DbDependency, user: UserDependency, _body: AssignUserModel
):
    project = db.query(Projects).filter_by(id=_body.project_id).first()
    victim_user = action_user = db.query(User).filter_by(id=_body.user_id).first()
    project.users.append(victim_user)
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

    available_employees = []

    for i in organization.employees:
        if _body.partially_available:
            pass
        if _body.close_to_finish:
            for j in i.projects:
                d1 = j.deadline_date
                d2 = date.today()

                monday1 = d2 - timedelta(days=d2.weekday())
                monday2 = d1 - timedelta(days=d1.weekday())

                # Calculate the difference in weeks
                weeks_difference = (monday2 - monday1).days // 7
                print(weeks_difference)

                if weeks_difference < _body.deadline:
                    available_employees.append(i)

        if _body.unavailable:
            pass
        if not i.projects:
            available_employees.append(i)

    return available_employees
