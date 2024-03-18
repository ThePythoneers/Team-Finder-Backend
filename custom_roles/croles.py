"""
croles.py includes everything related to custom roles including
creating, editing, deleting roles.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db import SESSIONLOCAL
from database.models import Custom_Roles, User, Projects, Users_Custom_Roles
from custom_roles.base_models import (
    AssignCustomRoleModel,
    CreateCustomRoleModel,
    EditCustomRoleModel,
)
from auth import authentication

router = APIRouter(tags={"Custom Roles"}, prefix="/roles/custom")


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


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_role(user: UserDependency, db: DbDependency, _body: CreateCustomRoleModel):
    """
    Create a custom role.
    """
    action_user = db.query(User).filter_by(id=user["id"]).first()

    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Only an Organization Admin is able to create custom roles.",
        )

    check_duplicate = (
        db.query(Custom_Roles)
        .filter_by(
            custom_role_name=_body.role_name,
            organization_id=str(action_user.organization_id),
        )
        .first()
    )

    if check_duplicate:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="A custom team role with the same name already exists.",
        )

    new_role = Custom_Roles(
        custom_role_name=_body.role_name,
        organization_id=action_user.organization_id,
    )
    db.add(new_role)
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK, content="Role created succesfully."
    )


@router.post("/user")
def assign_role_to_user(
    user: UserDependency, db: DbDependency, _body: AssignCustomRoleModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=_body.user_id).first()
    project = db.query(Projects).filter_by(id=_body.project_id).first()
    custom_role = db.query(Custom_Roles).filter_by(id=_body.role_id).first()
    role_check = (
        db.query(Users_Custom_Roles)
        .filter_by(
            user_id=_body.user_id,
            custom_role_id=_body.role_id,
            project_id=_body.project_id,
        )
        .first()
    )
    if not custom_role or not project or not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="The fields introduced cannot be found in the database.",
        )
    if role_check:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This role has already been assigned to this user.",
        )
    if (
        victim_user.organization_id != project.organization_id
        and project.organization_id != custom_role.organization_id
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="The fields specified are not from the same organization.",
        )

    if action_user.organization_id != victim_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is not from your organization.",
        )

    create_user_custom_role_model = Users_Custom_Roles(
        user_id=_body.user_id, project_id=_body.project_id, custom_role_id=_body.role_id
    )

    if not "Project Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Only a Project Manager can assign roles to an user.",
        )

    db.add(create_user_custom_role_model)
    db.commit()


@router.delete("/user")
def delete_role_from_user(
    user: UserDependency, db: DbDependency, _body: AssignCustomRoleModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=_body.user_id).first()
    project = db.query(Projects).filter_by(id=_body.project_id).first()
    custom_role = db.query(Custom_Roles).filter_by(id=_body.role_id).first()
    if not custom_role or not project or not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="The fields introduced cannot be found in the database.",
        )

    if (
        victim_user.organization_id != project.organization_id
        and project.organization_id != custom_role.organization_id
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="The fields specified are not from the same organization.",
        )

    if action_user.organization_id != victim_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is not from your organization.",
        )
    if not "Project Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Only a Project Manager can assign roles to an user.",
        )
    db.query(Users_Custom_Roles).filter_by(
        project_id=_body.project_id, custom_role_id=_body.role_id, user_id=_body.user_id
    ).delete()
    db.commit()


@router.get("/user")
def get_all_roles_from_user(user: UserDependency, db: DbDependency, _id: UUID):
    roles = db.query(Users_Custom_Roles).filter_by(user_id=_id).all()
    return_list = list()
    for i in roles:
        role_name = db.query(Custom_Roles).filter_by(id=i.custom_role_id).first()
        if not role_name:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content="Unexpected error for skills, a non-existing skill has been assigned to an user",
            )
        return_list.append(
            {
                "role_name": role_name.custom_role_name,
                "role_id": str(i.custom_role_id),
            }
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_list)


@router.get("/")
def get_all_custom_roles(user: UserDependency, db: DbDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    roles = (
        db.query(Custom_Roles)
        .filter_by(organization_id=str(action_user.organization_id))
        .all()
    )
    if roles:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(roles)
        )
    return []


@router.patch("/")
def edit_custom_role(
    db: DbDependency, user: UserDependency, _body: EditCustomRoleModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Only an Organization admin can edit team roles.",
        )
    role = db.query(Custom_Roles).filter_by(id=_body.role_id).first()
    if not role:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This custom role does not exist.",
        )
    role.custom_role_name = _body.role_name
    db.commit()


@router.delete("/")
def delete_custom_role(user: UserDependency, db: DbDependency, _id: UUID):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Only an Organization admin can delete team roles.",
        )
    db.query(Custom_Roles).filter_by(id=_id).delete()
    db.commit()
