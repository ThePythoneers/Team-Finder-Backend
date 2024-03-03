from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from roles.base_models import ModifyRoleModel
from auth import authentication
from database.models import User, Primary_Roles
from database.db import SESSIONLOCAL


router = APIRouter(prefix="/roles", tags={"Main Roles"})


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


@router.post("/assign")
def assign_role_to_user(db: DbDependency, user: UserDependecy, _body: ModifyRoleModel):
    return assign_role(db, user, _body.user_id, _body.role_name, True)


@router.put("/remove")
def remove_role_from_user(
    db: DbDependency, user: UserDependecy, _body: ModifyRoleModel
):
    if not _body.role_name in [
        "Employee",
        "Project Manager",
        "Department Manager",
        "Organization Admin",
    ]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="This role does not exist or malformed request.",
        )

    if _body.role_name == "Employee":
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot remove the role of Employee from someone.",
        )

    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=_body.user_id).first()
    role_to_delete = (
        db.query(Primary_Roles).filter_by(role_name=_body.role_name).first()
    )
    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="This user does not exist."
        )

    if action_user.organization_id != victim_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not allowed to modify the role of an user from another organization.",
        )

    if not "Organization Admin" in [i.role_name for i in victim_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only an Organization Admin can modify the role of an user.",
        )

    victim_user.primary_roles.remove(role_to_delete)
    db.commit()


def assign_role(db, user, user_id, _role_name, is_in_registration):

    if not _role_name in [
        "Employee",
        "Project Manager",
        "Department Manager",
        "Organization Admin",
    ]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="This role does not exist or malformed request.",
        )

    if _role_name == "Employee":
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot add the role of an employee to someone.",
        )

    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=user_id).first()
    role_to_add = db.query(Primary_Roles).filter_by(role_name=_role_name).first()

    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="This user does not exist."
        )

    if action_user.organization_id != victim_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not allowed to modify the role of an user from another organization.",
        )

    if not is_in_registration and not "Organization Admin" in [
        i.role_name for i in action_user.primary_roles
    ]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only an Organization Admin can modify the role of an user.",
        )

    if role_to_add in action_user.primary_roles:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Cannot assign an already assigned role to this user.",
        )

    victim_user.primary_roles.append(role_to_add)
    db.commit()
