from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db import SESSIONLOCAL
from database.models import TechnologyStack, User, Projects
from technology_stack.base_models import AssignTStackModel, CreateTStackModel
from auth import authentication

router = APIRouter(tags={"Technology Stack"}, prefix="/technology")


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


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_technology_stack(
    user: UserDependency, db: DbDependency, _body: CreateTStackModel
):
    """
    Create a custom role.
    """
    action_user = db.query(User).filter_by(id=user["id"]).first()
    check_duplicate = (
        db.query(TechnologyStack)
        .filter_by(
            tech_name=_body.technology_name, organization_id=action_user.organization_id
        )
        .first()
    )

    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Only an Organization Admin is able to create technology stacks.",
        )

    if check_duplicate:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="A technology stack with the same name already exists.",
        )

    create_tech_model = TechnologyStack(
        tech_name=_body.technology_name, organization_id=action_user.organization_id
    )
    db.add(create_tech_model)
    db.commit()

    return "Created"


@router.post("/assign")
def assign_technology_stack_to_project(
    user: UserDependency, db: DbDependency, _body: AssignTStackModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(id=_body.project_id).first()
    tech_stack = db.query(TechnologyStack).filter_by(id=_body.tech_id).first()

    if (
        tech_stack.organization_id != project.organization_id
        and project.organization_id != action_user.organization_id
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="The fields specified are not from the same organization.",
        )

    if not "Project Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only a Project Manager can assign technology stacks to a project.",
        )
    if tech_stack in project.technologies:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This Technology Stack has already been assigned to this project.",
        )
    project.technologies.append(tech_stack)

    db.commit()

    return JSONResponse(status_code=status.HTTP_200_OK, content="Assigned succesfully.")


@router.delete("/project")
def delete_technology_stack_from_project(
    user: UserDependency, db: DbDependency, _body: AssignTStackModel
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(id=_body.project_id).first()
    tech_stack = db.query(TechnologyStack).filter_by(id=_body.tech_id).first()

    if (
        tech_stack.organization_id != project.organization_id
        and project.organization_id != action_user.organization_id
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="The fields specified are not from the same organization.",
        )

    if not "Project Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Only a Project Manager can delete technology stacks from a project.",
        )
    if not tech_stack in project.technologies:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Bro this Technology Stack isn't even in the project technologies, wtfyd?",
        )
    project.technologies.remove(tech_stack)
    db.commit()

    return JSONResponse(status_code=status.HTTP_200_OK, content="Deleted succesfully.")


@router.get("/user")
def get_all_technology_stacks_from_project(
    user: UserDependency, db: DbDependency, _id: UUID
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(id=_id).first()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"technologies": [i.tech_name for i in project.technologies]},
    )


@router.get("/")
def get_all_technology_stacks(user: UserDependency, db: DbDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    technologies = (
        db.query(TechnologyStack)
        .filter_by(organization_id=str(action_user.organization_id))
        .all()
    )
    # if not technologies:
    #     return JSONResponse(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         content="There aren't any technology stacks in this organization yet.",
    #     )
    return_list = [
        {"id": str(i.id), "technology_name": i.tech_name} for i in technologies
    ]
    if return_list:
        return JSONResponse(status_code=status.HTTP_200_OK, content=return_list)
    return []


@router.delete("/")
def delete_technology_stack(user: UserDependency, db: DbDependency, _id: UUID):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    if not "Organization Admin" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Only an Organization admin can delete team roles.",
        )
    db.query(TechnologyStack).filter_by(id=_id).delete()
    db.commit()
