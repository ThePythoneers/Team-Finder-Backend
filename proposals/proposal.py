from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


from auth import authentication
from database.models import (
    AllocationProposal,
    Custom_Roles,
    DeallocationProposal,
    Notifications,
    Projects,
    User,
    Users_Custom_Roles,
    WorkHours,
)
from database.db import SESSIONLOCAL
from proposals.base_models import CreateAllocationProposal, CreateDeallocationProposal

router = APIRouter(prefix="/proposal", tags={"Proposals"})


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


@router.post("/allocation")
def create_allocation_proposal(
    db: DbDependency, user: UserDependency, _body: CreateAllocationProposal
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(id=_body.project_id).first()
    victim_user = db.query(User).filter_by(id=_body.user_id).first()

    if not "Project Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Project Managers are able to propose users.",
        )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not managing any projects right now.",
        )
    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user does not exist.",
        )
    if not victim_user.organization_id == action_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is not from your organization.",
        )
    if victim_user in project.users:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user has already been assigned to this project.",
        )
    if not 1 < _body.work_hours < 9:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Work hours must be a value in [1-8].",
        )
    check_proposal = (
        db.query(AllocationProposal)
        .filter_by(user_id=_body.user_id, project_id_allocation=project.id)
        .first()
    )
    if check_proposal:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="A proposal for this user and project has already been created.",
        )
    create_proposal_model = AllocationProposal(
        project_id_allocation=project.id,
        user_id=_body.user_id,
        comments=_body.comment,
        work_hours=_body.work_hours,
    )

    for i in _body.roles:
        role = db.query(Custom_Roles).filter_by(id=i).first()
        if not project in role.projects:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="This role is not from this project.",
            )
        if not role:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content="One or more role do not exist.",
            )
        create_proposal_model.roles.append(role)

    if not victim_user.department:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This user is not in any departments.",
        )
    create_notification_model = Notifications(
        type="ALLOCATION",
        to_manager=victim_user.department.department_manager,
        for_user=victim_user.id,
    )
    db.add(create_notification_model)
    db.add(create_proposal_model)

    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="User has been proposed and an answer from the Department Manager is awaited.",
    )


@router.post("/deallocation")
def create_deallocation_proposal(
    db: DbDependency, user: UserDependency, _body: CreateDeallocationProposal
):
    # known issue: work_hours does not reset as intended
    action_user = db.query(User).filter_by(id=user["id"]).first()
    project = db.query(Projects).filter_by(id=_body.project_id).first()
    victim_user = db.query(User).filter_by(id=_body.user_id).first()
    if not "Project Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Project Managers are able to propose users.",
        )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not managing any projects right now.",
        )
    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user does not exist.",
        )
    if not victim_user.organization_id == action_user.organization_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is not from your organization.",
        )
    if not victim_user in project.users:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user is not in your project.",
        )
    check_proposal = (
        db.query(DeallocationProposal)
        .filter_by(user_id=_body.user_id, project_id_deallocation=project.id)
        .first()
    )
    if check_proposal:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="A proposal for this user and project has already been created.",
        )

    create_proposal_model = DeallocationProposal(
        project_id_deallocation=project.id,
        user_id=_body.user_id,
        reason=_body.comment,
    )
    create_notification_model = Notifications(
        type="DEALLOCATION",
        to_manager=victim_user.department.department_manager,
        for_user=victim_user.id,
    )
    db.add(create_notification_model)
    db.add(create_proposal_model)

    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="User has been proposed and an answer from the Department Manager is awaited.",
    )


@router.get("/allocation/{_id}")
def get_allocation_proposal_from_user(
    db: DbDependency, user: UserDependency, _id: UUID
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=_id).first()

    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="This user does not exist."
        )
    if not action_user.department_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not managing any departments yet.",
        )
    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Department Managers can see someone's proposals.",
        )
    if not victim_user.department_id == action_user.department_id:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This user is not from your department.",
        )

    proposals = db.query(AllocationProposal).filter_by(user_id=_id).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[
            {
                "proposal_id": str(i.id),
                "project_id": str(i.project_id_allocation),
                "user_id": str(i.user_id),
                "comments": i.comments,
                "work_hours": i.work_hours,
                "proposed_roles": [str(j.id) for j in i.roles],
            }
            for i in proposals
        ],
    )


@router.get("/deallocation/{_id}")
def get_deallocation_proposal_from_user(
    db: DbDependency, user: UserDependency, _id: UUID
):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    victim_user = db.query(User).filter_by(id=_id).first()

    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content="This user does not exist."
        )
    if not action_user.department_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not managing any departments yet.",
        )
    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Department Managers can see someone's proposals.",
        )
    if not victim_user.department_id == action_user.department_id:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This user is not from your department.",
        )
    proposals = db.query(DeallocationProposal).filter_by(user_id=_id).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[
            {
                "proposal_id": str(i.id),
                "project_id": str(i.project_id_deallocation),
                "user_id": str(i.user_id),
                "reason": i.reason,
            }
            for i in proposals
        ],
    )


@router.get("/alloc-department/{_id}")
def get_allocation_proposal_from_department(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    users = db.query(User).filter_by(department_id=action_user.department_id).all()
    if not users:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Your department does not have users.",
        )
    if not action_user.department_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not managing any departments yet.",
        )
    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Department Managers can see someone's proposals.",
        )

    proposals = []
    for i in users:
        for j in db.query(AllocationProposal).filter_by(user_id=i.id).all():
            proposals.append(j)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[
            {
                "proposal_id": str(i.id),
                "project_id": str(i.project_id_allocation),
                "user_id": str(i.user_id),
                "comments": i.comments,
                "work_hours": i.work_hours,
                "proposed_roles": [str(j.id) for j in i.roles],
            }
            for i in proposals
        ],
    )


@router.get("/dealloc-department/{_id}")
def get_deallocation_proposal_from_department(db: DbDependency, user: UserDependency):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    users = db.query(User).filter_by(department_id=action_user.department_id).all()
    if not users:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Your department does not have users.",
        )
    if not action_user.department_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="You are not managing any departments yet.",
        )
    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Department Managers can see someone's proposals.",
        )

    proposals = []
    for i in users:
        for j in db.query(DeallocationProposal).filter_by(user_id=i.id).all():
            proposals.append(j)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=[
            {
                "proposal_id": str(i.id),
                "project_id": str(i.project_id_deallocation),
                "project_id": str(i.project_id_deallocation),
                "user_id": str(i.user_id),
                "reason": i.reason,
            }
            for i in proposals
        ],
    )


@router.post("/allocation/accept")
def accept_allocation_proposal(db: DbDependency, user: UserDependency, _id: UUID):
    action_user = db.query(User).filter_by(id=user["id"]).first()
    proposal = db.query(AllocationProposal).filter_by(id=_id).first()

    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Department Managers can see someone's proposals.",
        )

    if not proposal:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This proposal has already been settled or it does not exist.",
        )

    project = db.query(Projects).filter_by(id=proposal.project_id_allocation).first()

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This project does not exist.",
        )

    victim_user = db.query(User).filter_by(id=proposal.user_id).first()

    if not victim_user.department_id == action_user.department_id:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This user is not from your department.",
        )

    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="The proposed user does not exist.",
        )

    if victim_user in project.users:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user has already been assigned to this project.",
        )

    project.users.append(victim_user)
    work_hours = WorkHours(
        user_id=victim_user.id, project_id=project.id, work_hours=proposal.work_hours
    )
    db.delete(proposal)
    db.add(work_hours)
    db.commit()


@router.post("/allocation/reject")
def reject_allocation_proposal(db: DbDependency, user: UserDependency, _id: UUID):
    proposal = db.query(AllocationProposal).filter_by(id=_id).first()
    if not proposal:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This proposal does not exist.",
        )
    db.delete(proposal)
    db.commit()


@router.post("/deallocation/accept")
def accept_deallocation_proposal(db: DbDependency, user: UserDependency, _id: UUID):
    proposal = db.query(DeallocationProposal).filter_by(id=_id).first()
    action_user = db.query(User).filter_by(id=user["id"]).first()

    print(proposal.__dict__)
    if not "Department Manager" in [i.role_name for i in action_user.primary_roles]:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="Only Department Managers can see someone's proposals.",
        )

    if not proposal:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This proposal has already been settled or it does not exist.",
        )

    project = db.query(Projects).filter_by(id=proposal.project_id_deallocation).first()

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This project does not exist.",
        )

    victim_user = db.query(User).filter_by(id=proposal.user_id).first()

    if not victim_user.department_id == action_user.department_id:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="This user is not from your department.",
        )

    if not victim_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="The proposed user does not exist.",
        )

    if not victim_user in project.users:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content="This user has not been assigned to your project.",
        )

    project.users.remove(victim_user)
    project.deallocated_users.append(victim_user)
    work_hours = (
        db.query(WorkHours)
        .filter_by(user_id=victim_user.id, project_id=project.id)
        .first()
    )
    roles = (
        db.query(Users_Custom_Roles)
        .filter_by(user_id=victim_user.id, project_id=project.id)
        .all()
    )

    if roles:
        for i in roles:
            db.delete(i)
    db.delete(work_hours)
    db.delete(proposal)
    db.commit()


@router.post("/deallocation/reject")
def reject_deallocation_proposal(db: DbDependency, user: UserDependency, _id: UUID):
    db.query(DeallocationProposal).filter_by(id=_id).delete()
    db.commit()
