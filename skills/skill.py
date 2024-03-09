from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.models import Skill, Skill_Category, User, User_Skills
from database.db import SESSIONLOCAL
from auth import authentication
from skills.base_models import CreateSkillModel


router = APIRouter(prefix="/skill", tags={"Skills"})


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


@router.post("/")
def create_skill(db: DbDependency, user: UserDependency, _body: CreateSkillModel):
    action_user = db.query(User).filter_by(id=user["id"]).first()

    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only a department manager can modify skills.",
        )

    create_skill_model = Skill(
        skill_name=_body.skill_name,
        skill_description=_body.description,
        organization_id=action_user.organization_id,
        author=_body.author,
    )
    create_skill_model.skill_category = _body.skill_category
    db.add(create_skill_model)
    db.commit()


@router.delete("/")
def delete_skill(db: DbDependency, user: UserDependency, _id: UUID):
    action_user = db.query(User).filter_by(id=user["id"]).first()

    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only a department manager can modify skills.",
        )
    if db.query(User_Skills).filter_by(skill_id=_id).first():
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You have to remove the role from all employees before deleting it.",
        )
    db.query(Skill).filter_by(id=_id).delete()
    db.commit()


@router.post("/category/{name}")
def create_skill_category(db: DbDependency, user: UserDependency, name: str):
    action_user = db.query(User).filter_by(id=user["id"]).first()

    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only a department manager can modify skills.",
        )

    create_skill_category_model = Skill_Category(
        category_name=name, organization_id=action_user.organization_id
    )

    db.add(create_skill_category_model)
    db.commit()


@router.get("/category/")
def get_skill_categories(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    categories = (
        db.query(Skill_Category)
        .filter_by(organization_id=action_user.organization_id)
        .all()
    )
    return categories


@router.get("/")
def get_all_skills(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    skills = (
        db.query(Skill).filter_by(organization_id=action_user.organization_id).all()
    )
    return skills
