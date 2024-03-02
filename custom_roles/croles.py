"""
croles.py includes everything related to custom roles including
creating, editing, deleting roles.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db import SESSIONLOCAL
from database.models import Custom_Roles, User
from custom_roles.base_models import CustomRole, GetCRolesRequest
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


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_role(
    user: UserDependency, db: DbDependency, create_role_request: CustomRole
):
    """
    Create a custom role.
    """
    user = db.query(User).filter_by(id=user["id"]).first()

    if str(user.organization_id) != create_role_request.organization_id:
        print(db.query(User).filter_by(id=user["id"]).first().organization_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have access to this organization",
        )

    role_model = Custom_Roles(
        organization_id=create_role_request.organization_id,
        custom_role_name=create_role_request.role_name,
    )
    db.add(role_model)
    db.commit()


@router.post("/get")
# pylint: disable=unused-argument
def get_roles(user: UserDependency, db: DbDependency, request: GetCRolesRequest):
    """
    Get all roles from an organization.
    """
    roles = (
        db.query(Custom_Roles).filter_by(organization_id=request.organization_id).all()
    )

    roles_dict = {}
    for j, i in enumerate(roles):
        roles_dict[j] = {
            "custom_role_name": i.custom_role_name,
            "id": str(i.id),
            "organization_id": str(i.organization_id),
        }

    return JSONResponse(content=roles_dict, status_code=200)
