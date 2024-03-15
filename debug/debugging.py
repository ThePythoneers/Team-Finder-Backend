from typing import Annotated


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from auth import authentication

from database.db import SESSIONLOCAL
from database.models import Primary_Roles, User

router = APIRouter(prefix="/debug", tags={"Debugging"})


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


@router.post("/DEBUG_ALL_PRIMARY_ROLES")
def primary(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    roles = db.query(Primary_Roles).all()

    for i in roles:
        if i not in action_user.primary_roles:
            action_user.primary_roles.append(i)

    db.commit()
