from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.models import (
    Department,
    Department_projects,
    Skill,
    Skill_Category,
    User,
    User_Skills,
)
from database.db import SESSIONLOCAL
from auth import authentication
from skills.base_models import CreateSkillModel, EditSkillCategoryModel


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
    check_name = db.query(Skill).filter_by(skill_name=_body.skill_name).first()

    if check_name:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="A skill with the same name already exists.",
        )

    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only a department manager can modify skills.",
        )

    create_skill_model = Skill(
        skill_name=_body.skill_name,
        skill_description=_body.description,
        organization_id=action_user.organization_id,
        author=action_user.id,
    )

    if _body.department_id:
        department = db.query(Department).filter_by(id=_body.department_id).first()
        if department:
            create_skill_model.departments.append(department)

    for i in _body.skill_category:
        if not db.query(Skill_Category).filter_by(id=i).first():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="One or more skills do not exist.",
            )
    create_skill_model.skill_category = _body.skill_category

    db.add(create_skill_model)
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK, content="Skill created successfully."
    )


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
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content="Deleted.")


@router.post("/category/{name}")
def create_skill_category(db: DbDependency, user: UserDependency, name: str):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    name_check = db.query(Skill_Category).filter_by(category_name=name).first()

    if name_check:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This Skill Category already exists.",
        )

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

    return JSONResponse(
        status_code=status.HTTP_200_OK, content="Skill category created succesfully."
    )


@router.patch("/category/")
def edit_skill_cateogry(
    db: DbDependency, user: UserDependency, _body: EditSkillCategoryModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    name_check = (
        db.query(Skill_Category).filter_by(category_name=_body.category_name).first()
    )
    category = db.query(Skill_Category).filter_by(id=_body.category_id).first()

    if not category:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This skill category does not exist.",
        )
    if name_check:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This Skill Category already exists.",
        )

    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only a department manager can modify skill categories.",
        )

    category.category_name = _body.category_name

    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK, content="Skill category edited succesfully."
    )


@router.delete("/category/{_id}")
def delete_skill_category(db: DbDependency, user: UserDependency, _id: str):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    category = db.query(Skill_Category).filter_by(id=_id)
    can_delete = (
        db.query(Skill).filter_by(organization_id=action_user.organization_id).first()
    )

    if can_delete:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You cannot delete this skill category because it's being used in one or more skills.",
        )
    if not category.first():
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This Skill Category doesn't exist.",
        )

    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only a department manager can modify skills.",
        )

    category.delete()

    db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content="Skill category deleted."
    )


@router.get("/categories/")
def get_skill_categories(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    categories = (
        db.query(Skill_Category)
        .filter_by(organization_id=action_user.organization_id)
        .all()
    )
    return_list = []
    for i in categories:
        return_list.append(
            {
                "id": i.id,
                "category_name": i.category_name,
                "organization_id": i.organization_id,
            }
        )
    return return_list


@router.get("/category/{_id}")
def get_skill_category_by_id(db: DbDependency, user: UserDependency, _id: str):
    category = db.query(Skill_Category).filter_by(id=_id).first()
    action_user = db.query(User).filter_by(id=user["id"]).first()
    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not allowed to do this.",
        )
    if not category:
        return []
    return category


@router.get("/")
def get_all_skills(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    skills = (
        db.query(Skill).filter_by(organization_id=action_user.organization_id).all()
    )

    return_list = []

    for i in skills:
        return_list.append(
            {
                "skill_category": i.skill_category,
                "skill_name": i.skill_name,
                "organization_id": i.organization_id,
                "author": i.author,
                "id": i.id,
                "skill_description": i.skill_description,
                "departments": [j.id for j in i.departments],
            }
        )
    return return_list


@router.get("/department")
def get_all_skills_from_department(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()

    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only a department manager can view this data.",
        )

    department = db.query(Department).filter_by(id=action_user.department_id).first()

    if not department:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not managing any departments right now.",
        )

    return_list = []

    for i in department.skills:
        return_list.append(
            {
                "skill_category": i.skill_category,
                "skill_name": i.skill_name,
                "organization_id": i.organization_id,
                "author": i.author,
                "id": i.id,
                "skill_description": i.skill_description,
            }
        )

    return return_list


@router.post("/verify/{_id}")
def verify_skill(db: DbDependency, user: UserDependency, _id: UUID):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    user_skill = db.query(User_Skills).filter_by(id=_id).first()
    victim_user = db.query(User).filter_by(id=user_skill.user_id).first()

    if not victim_user.organization_id == action_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is not in your organization.",
        )

    if not victim_user.department_id == action_user.department_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is not in your department.",
        )

    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Department Managers are allowed to verify skills.",
        )

    user_skill.verified = not user_skill.verified
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=f"Skill {'un' if not user_skill.verified else ''}verified",
    )


@router.get("/verify")
def get_all_unverified_skills(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()

    if not action_user.department:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You don't have the required permission to do this.",
        )

    users = db.query(User).filter_by(department_id=action_user.department_id).all()

    if not users:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="You don't have any users in this department.",
        )
    roles = []
    for i in users:
        user_roles = db.query(User_Skills).filter_by(user_id=i.id, verified=False).all()
        print(i.username)
        print(user_roles)
        for j in user_roles:
            roles.append(j)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[
            {
                "id": str(i.id),
                "skill_level": i.skill_level,
                "training_title": i.training_title if i.training_title else None,
                "project_link": i.project_link if i.project_link else None,
                "user_id": str(i.user_id),
                "skill_id": str(i.skill_id),
                "skill_experience": i.skill_experience,
                "training_description": (
                    i.training_description if i.training_description else None
                ),
                "verified": i.verified,
            }
            for i in roles
        ],
    )
