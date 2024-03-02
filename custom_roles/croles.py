from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from sqlalchemy.orm import Session
from database.db import SESSIONLOCAL
from database.models import Custom_Roles, User
from custom_roles.baseModels import CustomRole, GetCRolesRequest
from auth import authentication

router = APIRouter(
    tags={"Custom Roles"},
    prefix="/roles/custom"
    )

def get_db():
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(authentication.get_current_user)]

@router.post("/create", status_code= status.HTTP_201_CREATED)
def create_role(user: user_dependency, db: db_dependency, create_role_request: CustomRole):
    user = db.query(User).filter_by(id = user["id"]).first()
    
    if str(user.organization_id) != create_role_request.organization_id:
        print(db.query(User).filter_by(id = user["id"]).first().organization_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have access to this organization")
    
    role_model = Custom_Roles(
        organization_id = create_role_request.organization_id,
        custom_role_name = create_role_request.role_name
    )
    db.add(role_model)
    db.commit()

@router.post("/get")
def get_roles(user:user_dependency, db:db_dependency, request: GetCRolesRequest):
    roles = db.query(Custom_Roles).filter_by(organization_id = request.organization_id).all()
    return JSONResponse(
        content = roles,
        status_code = 200
        )
    
