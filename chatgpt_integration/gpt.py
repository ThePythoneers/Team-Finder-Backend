from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from auth import authentication
from sqlalchemy.orm import Session
from database.db import SESSIONLOCAL

from chatgpt_integration.base_models import GetChatGPTInfo
from database.models import Organization, User

from utils.chatgpt import chatgpt

router = APIRouter(tags={"Chat GPT"}, prefix="/gpt")


def get_db():
    """
    creates a db session
    """
    try:
        db = SESSIONLOCAL()
        yield db
        print("test")
    finally:
        db.close()


DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(authentication.get_current_user)]

@router.post("/additional-context")
def get_additional_context_from_database(
    db: DbDependency, user: UserDependency, _body: GetChatGPTInfo
):

    action_user = db.query(User).filter_by(id=user["id"]).first()

    organization = db.query(Organization).filter_by(id=action_user.organization_id).first()

    if not organization:
        return JSONResponse(
            status_code=404, content="this organization does not exist."
        )

    employees_list = []
    for i in organization.employees:
        employees_list.append({
            "user_name": i.username
        })

    return chatgpt(_body.message, employees_list)


