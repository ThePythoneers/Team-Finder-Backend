"""
organizations.py hosts everything related to organizations, getting, editing information
related to itself.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


from auth import authentication
from database.models import User, Organization
from database.db import SESSIONLOCAL
from utils.utility import create_link_ref

router = APIRouter(prefix="/organization", tags={"Organization"})


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


@router.get("/link/{ref}")
def get_organization_info_from_ref(db: DbDependency, ref: str):
    """
    Gets information for the registration page from the refferal.
    """
    db_org = db.query(Organization).filter_by(custom_link=ref).first()

    if not db_org:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This organization does not exist.",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "organization_name": db_org.organization_name,
            "hq_address": db_org.hq_address,
        },
    )


@router.get("/")
def get_organization_info(db: DbDependency, user: UserDependecy, org: UUID):
    """
    Gets information for the organization page from the id.
    """
    try:
        UUID(str(org), version=4)
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="invalid uuid"
        )

    action_user = db.query(User).filter_by(id=user["id"]).first()
    db_org = db.query(Organization).filter_by(id=org).first()

    if not db_org:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This organization does not exist.",
        )

    if action_user.organization_id != org:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot view information about an organization other than yours.",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "organization_id": str(db_org.id),
            "organization_name": db_org.organization_name,
            "hq_address": db_org.hq_address,
            "owner_id": str(db_org.owner_id),
            "employees": [str(i.id) for i in db_org.employees],
            "created_at": str(db_org.created_at),
            "link_ref": db_org.custom_link,
        },
    )


@router.put("/ref/refresh")
def refresh_ref_link(db: DbDependency, user: UserDependecy):
    action_user = db.query(User).filter_by(id=user["id"]).first()

    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=200,
            content="Only an Organization Admin can refresh the refferal.",
        )
    db_org = db.query(Organization).filter_by(id=action_user.organization_id).first()
    db_org.custom_link = create_link_ref(10)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"refferal": db_org.custom_link}
    )


@router.get("/employees")
def get_employees_from_organization(db: DbDependency, user: UserDependecy):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    db_org = db.query(Organization).filter_by(id=action_user.organization_id).first()
    return_list = []

    for j in db_org.employees:
        return_list.append(
            {
                "id": str(j.id),
                "username": j.username,
                "email": j.email,
                "primary_roles": [i.role_name for i in j.primary_roles],
                "department_id": str(j.department_id) if j.department_id else None,
                "organization_id": str(j.organization_id),
                "work_hours": 0,
            }
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=return_list)
