from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from database.db import SESSIONLOCAL
from sqlalchemy.orm import Session
from database.models import Users
from auth import authentication
from account.models import RoleRequestModel

router = APIRouter(prefix = "/user")

def get_db():
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(authentication.get_current_user)]

@router.post("/{user}")
async def get_user_info(db: db_dependency,auth: user_dependency, user: str):

    user = db.query(Users).filter(Users.uuid == user).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = "This account does not exist.")
    user_data = {
        "name": user.username,
        "email": user.email,
        "roles": user.roles,
        "organization": user.organization_name,
        "address": user.hq_address,
        "type": user.type_
    }
    return user_data

@router.post("/roles/edit")
async def set_user_role(db: db_dependency, auth: user_dependency, roles: RoleRequestModel):
    # user = db.query(Users).filter(Users.uuid == roles.user_id).first()
    # user.roles = "".join(i for i in roles.roles)
    # db.commit()
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)