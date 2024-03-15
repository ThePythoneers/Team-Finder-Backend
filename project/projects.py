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
    if (_body.deadline_date - _body.start_date).total_seconds() < 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="The deadline cannot be assigned before the start of the project.",
        )
    if _body.work_hours <= 0 or _body.work_hours > 8:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Work hours needs to be a value between 1 and 8",
        )
    create_project_model = Projects(
        project_name=_body.project_name,
        project_period=_body.project_period,
        project_status=_body.project_status,
        description=_body.general_description,
        start_date=_body.start_date,
        deadline_date=_body.deadline_date,
        work_hours=_body.work_hours,
        organization_id=action_user.organization_id,
    )

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

    if _body.work_hours:
        if _body.work_hours < 0 or _body.work_hours > 8:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content="Work hours needs to be a value between 1 and 8",
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
        update_dict["description"] = _body.general_description
    if _body.technology_stack:
        for i in _body.technology_stack:
            create_tech_model = TechnologyStack(
                tech_name=i, organization_id=action_user.organization_id
            )
            tech = project_id.first()  # Garbage collection bug
            tech.technologies.append(create_tech_model)
    if _body.work_hours:
        update_dict["work_hours"] = _body.work_hours
        for i in project_id.first().users:
            i.work_hours += _body.work_hours - project_id.first().work_hours
    if _body.team_roles:
        for i in _body.technology_stack:
            custom_role = db.query(Custom_Roles).filter_by(i.id).first()
            tech = project_id.first()  # Garbage collection bug
            tech.project_roles.append(custom_role)
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

    available_employees = []

    for i in organization.employees:
        i.__dict__["method"] = []
        if _body.partially_available and i.work_hours < 8:
            i.__dict__["method"].append("partially_available")
            available_employees.append(i.__dict__)
            print("test")
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
        "users": [{"id": str(i.id), "username:": i.username} for i in project.users],
        "project_roles": [i.custom_role_name for i in project.project_roles],
        "work_hours": project.work_hours,
        "technology_stack": [i.tech_name for i in project.technologies],
        "deallocated_users": [
            {"id": str(i.id), "username:": i.username}
            for i in project.deallocated_users
        ],
    }

    return JSONResponse(status_code=200, content=project_dict)


@router.get("/all/")
def get_all_projects_info(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    projects = (
        db.query(Projects).filter_by(organization_id=action_user.organization_id).all()
    )
    if not projects:
        return JSONResponse(
            status_code=404, content="This organization does not have any projects yet."
        )
    project_list = []
    for i in projects:
        project_list.append(
            {
                "project_id": str(i.id),
                "project_name": i.project_name,
                "project_period": i.project_period,
                "start_date": str(i.start_date),
                "deadline_date": str(i.deadline_date),
                "project_status": i.project_status,
                "description": i.description,
                "users": [{"id": str(i.id), "username:": i.username} for i in i.users],
                "project_roles": [i.custom_role_name for i in i.project_roles],
                "work_hours": i.work_hours,
                "technology_stack": [
                    {"technology_name": i.tech_name, "id": str(i.id)}
                    for i in i.technologies
                ],
                "deallocated_users": [
                    {"id": str(j.id), "username:": j.username}
                    for j in i.deallocated_users
                ],
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
