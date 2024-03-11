from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from departments.base_models import (
    AddUserToDepartmentModel,
    AssignManagerModel,
    CreateDepartmentModel,
    DeleteDepartmentModel,
    DeleteManagerModel,
)
from auth import authentication
from database.models import Organization, User, Department
from database.db import SESSIONLOCAL

router = APIRouter(prefix="/department", tags={"Department"})


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
def create_department(
    db: DbDependency, user: UserDependency, _body: CreateDepartmentModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only an Organization Admin can create a Department.",
        )
    check_department = (
        db.query(Department)
        .filter_by(
            department_name=_body.department_name,
            organization_id=action_user.organization_id,
        )
        .first()
    )
    if check_department:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="There already is a department with the same name.",
        )

    create_department_model = Department(
        department_name=_body.department_name,
        organization_id=action_user.organization_id,
    )

    db.add(create_department_model)
    db.commit()


@router.get("/")
def get_department_info(db: DbDependency, user: UserDependency, _id: str):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    department = db.query(Department).filter_by(id=_id).first()

    if not department:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This department does not exist.",
        )

    if department.organization_id != action_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot view the departments of another organization.",
        )

    return JSONResponse(
        status_code=200,
        content={
            "department_id": str(department.id),
            "department_name": department.department_name,
            "department_manager": department.department_manager,
            "organization_id": str(department.organization_id),
            "department_users": department.department_users,
            "skills": department.skills,
            "created_at": str(department.created_at),
        },
    )


@router.delete("/")
def delete_department(
    db: DbDependency, user: UserDependency, _body: DeleteDepartmentModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()

    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only an Organization Admin can delete a Department.",
        )

    check_department = (
        db.query(Department)
        .filter_by(
            id=_body.department_id,
            organization_id=action_user.organization_id,
        )
        .first()
    )

    if check_department.organization_id != action_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot delete departments from another organization.",
        )

    db.query(Department).filter_by(
        id=_body.department_id, organization_id=action_user.organization_id
    ).delete()
    db.commit()


@router.post("/manager/")
def assign_department_manager(
    db: DbDependency, user: UserDependency, _body: AssignManagerModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=_body.manager_id).first()
    department = db.query(Department).filter_by(id=_body.department_id).first()

    departments = (
        db.query(Department)
        .filter_by(organization_id=action_user.organization_id)
        .all()
    )

    for department in departments:
        if victim_user.id == department.department_manager:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="This user is already a manager for another department",
            )

    if not department:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="The department you provided does not exist.",
        )
    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only the Organization Admin can assign a Department Manager.",
        )

    if not "Department Manager" in [i.role_name for i in victim_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="The user you provided does not have the Department Manager role.",
        )

    if department.department_manager:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This department already has a manager assigned. \
                  Consider deleting him first the adding another person.",
        )

    if victim_user.organization_id != department.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot assign users from other organizations.",
        )

    department.department_manager = victim_user.id
    db.commit()


@router.delete("/manager/")
def delete_department_manager(
    db: DbDependency, user: UserDependency, _body: DeleteManagerModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    department = db.query(Department).filter_by(id=_body.department_id).first()

    if not department:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="The department you provided does not exist.",
        )
    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only the Organization Admin can delete a Department Manager.",
        )

    if not department.department_manager:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This department does not have any manager assigned.",
        )

    department.department_manager = None
    db.commit()


@router.get("/unassigned/")
def get_unassigned_departemnt_users(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    employees_db = (
        db.query(Organization)
        .filter_by(id=action_user.organization_id)
        .first()
        .employees
    )
    unassigned_employees = [i for i in employees_db if i.department_id is None]
    dict_employees = [i.__dict__ for i in employees_db if i.department_id is None]

    for i, j in zip(dict_employees, unassigned_employees):
        i.pop("hashed_password")
        i["primary_roles"] = j.primary_roles

    # nici nu stau sa descifrez dar la roles sa imi dai doar numele rolului nu doar id-ul
    # te ai trezit mai cu mot aici si ai zis sa imi dai si id-ul

    return unassigned_employees


@router.get("/users/{_id}")
def get_users_from_department(db: DbDependency, user: UserDependency, _id: UUID):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    employees_db = (
        db.query(Organization)
        .filter_by(id=action_user.organization_id)
        .first()
        .employees
    )

    departments = db.query(Department).filter_by(department_manager=user["id"])
    
    assigned_employees = [i for i in employees_db if i.department_id == _id]
    dict_employees = [i.__dict__ for i in employees_db if i.department_id == _id]

    if not assigned_employees:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This department doesn't have any employees assigned yet.",
        )

    for i, j in zip(dict_employees, assigned_employees):
        i.pop("hashed_password")
        i["primary_roles"] = j.primary_roles

    # nici nu stau sa descifrez dar la roles sa imi dai doar numele rolului nu doar id-ul
    # te ai trezit mai cu mot aici si ai zis sa imi dai si id-ul

    return assigned_employees


@router.post("/user")
def add_user_to_department(
    db: DbDependency, user: UserDependency, _body: AddUserToDepartmentModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=_body.user_id).first()
    department = (
        db.query(Department).filter_by(department_manager=victim_user.id).first()
    )

    if "Department Manager" not in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not a Department Manager",
        )
    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This user does not exist.",
        )

    if action_user.organization_id != victim_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot add an user from another organization to your department.",
        )

    if not victim_user.department_id is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is already in a department.",
        )

    if department:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is a Department Manager and cannot be added to the department.",
        )
    department = (
        db.query(Department).filter_by(department_manager=action_user.id).first()
    )

    if not department:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This department does not exist.",
        )

    department.department_users.append(victim_user)
    db.commit()


@router.delete("/user")
def remove_user_to_department(
    db: DbDependency, user: UserDependency, _body: AddUserToDepartmentModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=_body.user_id).first()

    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This user does not exist.",
        )

    if victim_user.department_id is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is not assigned to any department.",
        )

    if action_user.organization_id != victim_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot delete an user from another organization.",
        )

    department = db.query(Department).filter_by(id=action_user.department_id).first()

    if not department:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This department does not exist.",
        )

    department.department_users.remove(victim_user)
    db.commit()


@router.get("s")
def get_departments(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    departments = (
        db.query(Department)
        .filter_by(organization_id=action_user.organization_id)
        .all()
    )

    return_departments = []
    for i in departments:
        manager = db.query(User).filter_by(id=i.department_manager).first()
        manager_email = manager.email if manager else None
        return_departments.append(
            {
                "id": str(i.id),
                "department_name": i.department_name,
                "department_manager": (
                    str(i.department_manager) if i.department_manager else None
                ),
                "manager_email": manager_email,
                "department_users": [str(i.id) for i in i.department_users],
            }
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_departments)
