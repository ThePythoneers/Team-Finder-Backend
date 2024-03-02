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


@router.get("/get/link/{ref}")
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
        status_code=200,
        content={
            "organization_name": db_org.organization_name,
            "hq_address": db_org.hq_address,
        },
    )


@router.get("/get/{org}")
def get_organization_info(db: DbDependency, user: UserDependecy, org: str):
    """
    Gets information for the organization page from the id.
    """
    try:
        UUID(org)
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content="invalid uuid"
        )

    db_org = db.query(Organization).filter_by(id=org).first()

    if not db_org:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This organization does not exist.",
        )

    if str(db.query(User).filter_by(id=user["id"]).first().organization_id) != org:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot view information about an organization other than yours.",
        )

    return JSONResponse(
        status_code=200,
        content={
            "organization_id": str(db_org.id),
            "organization_name": db_org.organization_name,
            "hq_address": db_org.hq_address,
            "owner_id": str(db_org.owner_id),
            "employees": [str(i.id) for i in db_org.employees],
            "created_at": str(db_org.created_at),
        },
    )
