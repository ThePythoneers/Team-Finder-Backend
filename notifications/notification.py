from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

# from fastapi.websockets import WebSocket
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


from auth import authentication
from database.models import (
    Notifications,
    User,
)
from database.db import SESSIONLOCAL

# import asyncio

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


@router.get("/")
def get_notifications(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    notifications = db.query(Notifications).filter_by(to_manager=action_user.id).all()
    notifs = []

    for i in notifications:
        notifs.append(
            {
                "id": str(i.id),
                "type": i.type,
                "for_user": str(i.for_user),
                "has_been_read": i.sent,
            }
        )
        i.sent = True

    db.commit()

    return JSONResponse(status_code=status.HTTP_200_OK, content=notifs)


@router.delete("/")
def delete_notifications(db: DbDependency, user: UserDependency, _id: UUID):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    notifications = (
        db.query(Notifications).filter_by(to_manager=action_user.id, id=_id).first()
    )

    if not notifications:
        return JSONResponse("The notification you tried deleting does not exist.")

    db.delete(notifications)

    db.commit()


# class SingletonMeta(type):
#     """
#     A Singleton metaclass that creates a Singleton instance.
#     """

#     _instances = {}

#     def __call__(cls, *args, **kwargs):
#         """
#         If an instance of the class doesn't exist, create one. Otherwise, return the existing instance.
#         """
#         if cls not in cls._instances:
#             cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]


# class ConnectionManager(metaclass=SingletonMeta):
#     def __init__(self):
#         self.active_connections: {} = {}

#     async def connect(self, websocket: WebSocket, client_id: str):
#         await websocket.accept()
#         self.active_connections[client_id] = websocket
#         print(self.active_connections)

#     async def disconnect(self, websocket: WebSocket, client_id):
#         self.active_connections.pop(client_id)

#     async def broadcast(self, message: str, user):
#         connection = self.active_connections.get(user)
#         if connection:
#             # await connection.send_text(message)
#             await connection.send_json(message)
#             await connection.send_json("reset")
