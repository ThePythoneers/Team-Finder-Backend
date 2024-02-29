from database.models import *
from database.db import SESSIONLOCAL
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends


def get_db():
    try:
        db = SESSIONLOCAL()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def user_is_in_organization(db: db_dependency,user_id, org_id):
    user_org = db.query(User).filter_by(id = user_id).organization.id
    return user_org == org_id


user_is_in_organization(user_id = "1b997a57-7220-4941-a7f2-1977f94fecfc", org_id = "86e4d82d-7c2f-4926-aa43-93c053c51927")