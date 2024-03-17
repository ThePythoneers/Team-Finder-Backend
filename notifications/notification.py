from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.websockets import WebSocket
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session


from auth import authentication
from database.models import (
    AllocationProposal,
    Custom_Roles,
    Department,
    Notifications,
    Organization,
    TechnologyStack,
    User,
    Projects,
    WorkHours,
)
from database.db import SESSIONLOCAL
from project.base_models import (
    AddCustomRoleToProjectModel,
    AssignUserModel,
    CreateProjectModel,
    GetAvailableEmployeesModel,
    UpdateProjectModel,
)
from datetime import date, timedelta
import asyncio

router = APIRouter(prefix="/notifications", tags={"Notifications"})


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


@router.websocket("/ws")
async def get_notifications(websocket: WebSocket, db: DbDependency):
    await websocket.accept()
    user = authentication.get_current_user(websocket.headers["Authorization"])
    action_user = db.query(User).filter_by(id=user["id"]).first()
    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        await websocket.close(reason="Not a Department Manager")
        return 0
    if not action_user.department_id:
        await websocket.close(reason="Not managing any departments")
        return 0
    while True:
        print("WEBSOCKET: Run check for notifications")
        notifications = (
            db.query(Notifications)
            .filter_by(to_manager=action_user.id, sent=False)
            .all()
        )

        for i in notifications:
            i.sent = True
            await websocket.send_json({"type": i.type, "for_user": str(i.for_user)})
        db.commit()

        await asyncio.sleep(15)