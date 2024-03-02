from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from database.db import SESSIONLOCAL
from sqlalchemy.orm import Session
from typing import Annotated
from uuid import UUID

from auth import authentication
from database.models import User, Organization


router = APIRouter(
    prefix = "/organization",
    tags={"Organization"}
)

def get_db():
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(authentication.get_current_user)]


@router.get("/get/link/{ref}")
def get_organization_info_from_ref(db: db_dependency, ref: str):
    db_org = db.query(Organization).filter_by(custom_link = ref).first()

    if not db_org:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content = "This organization does not exist."
        )
    
    return JSONResponse(
        status_code = 200,
        content = {
            "organization_name" : db_org.organization_name,
            "hq_address" : db_org.hq_address,
        }
    )

@router.get("/get/{org}")
def get_organization_info(db: db_dependency, user: user_dependency, org: str):
    try:
        UUID(org)
    except:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content = "Invalid UUID"
        )

    db_org = db.query(Organization).filter_by(id = org).first()

    if not db_org:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content = "This organization does not exist."
        )
    
    if str(db.query(User).filter_by(id = user["id"]).first().organization_id) != org:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content = "You cannot view information about an organization other than yours."
        )
    
    return JSONResponse(
        status_code = 200,
        content = {
            "organization_id" : str(db_org.id),
            "organization_name" : db_org.organization_name,
            "hq_address" : db_org.hq_address,
            "owner_id" : str(db_org.owner_id),
            "employees": [str(i.id) for i in db_org.employees],
            "created_at": str(db_org.created_at)
            
        }
    )