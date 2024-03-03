from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from departments.base_models import (
    AssignManagerModel,
    CreateDepartmentModel,
    DeleteDepartmentModel,
    DeleteManagerModel,
)
from auth import authentication
from database.models import User, Department
from database.db import SESSIONLOCAL

# TODO Unintended behaviour between different departments and organizations.


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
UserDependecy = Annotated[dict, Depends(authentication.get_current_user)]


@router.post("/create")
def create_department(
    db: DbDependency, user: UserDependecy, _body: CreateDepartmentModel
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


@router.get("/get/{_id}")
def get_department_info(db: DbDependency, user: UserDependecy, _id: str):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    department = db.query(Department).filter_by(_id=id).first()

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


@router.put("/delete")
def delete_department(
    db: DbDependency, user: UserDependecy, _body: DeleteDepartmentModel
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


@router.post("/manager/assign")
def assign_department_manager(
    db: DbDependency, user: UserDependecy, _body: AssignManagerModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=_body.manager_id).first()
    department = db.query(Department).filter_by(id=_body.department_id).first()

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
            content="This department already has a manager assigned. Consider deleting him first the adding another person.",
        )

    if victim_user.organization_id != department.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot assign users from other organizations.",
        )

    department.department_manager = victim_user.id
    db.commit()


@router.put("/manager/delete")
def delete_department_manager(
    db: DbDependency, user: UserDependecy, _body: DeleteManagerModel
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
