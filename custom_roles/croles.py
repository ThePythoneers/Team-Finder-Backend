"""
croles.py includes everything related to custom roles including
creating, editing, deleting roles.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db import SESSIONLOCAL
from database.models import Custom_Roles, User, Projects, Users_Custom_Roles
from custom_roles.base_models import AssignCustomRoleModel, CreateCustomRoleModel
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
def create_role_in_project(
    user: UserDependency, db: DbDependency, _body: CreateCustomRoleModel
):
    """
    Create a custom role.
    """
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(id=_body.project_id).first()
    project.project_roles.append(
        Custom_Roles(
            custom_role_name=_body.role_name,
            organization_id=action_user.organization_id,
        )
    )
    db.commit()


@router.post("/user")
def assign_role_to_user(
    user: UserDependency, db: DbDependency, _body: AssignCustomRoleModel
):
    create_user_custom_role_model = Users_Custom_Roles(
        user_id=_body.user_id, project_id=_body.project_id, custom_role_id=_body.role_id
    )
    db.add(create_user_custom_role_model)
    db.commit()


@router.delete("/user")
def delete_role_from_user(
    user: UserDependency, db: DbDependency, _body: AssignCustomRoleModel
):
    db.query(Users_Custom_Roles).filter_by(
        project_id=_body.project_id, custom_role_id=_body.role_id, user_id=_body.user_id
    ).delete()
    db.commit()


@router.get("/user")
def get_all_role_from_user(user: UserDependency, db: DbDependency, _id: UUID):
    roles = db.query(Users_Custom_Roles).filter_by(user_id=_id).all()
    return_list = list()
    for i in roles:
        return_list.append(
            {
                "role_name": db.query(Custom_Roles)
                .filter_by(id=i.custom_role_id)
                .first()
                .custom_role_name,
                "role_id": str(i.custom_role_id),
            }
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content=return_list)
