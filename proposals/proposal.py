from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


from auth import authentication
from database.models import AllocationProposal, DeallocationProposal, Projects, User
from database.db import SESSIONLOCAL
from proposals.base_models import CreateAllocationProposal

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
    create_proposal_model = AllocationProposal(
        project_id_allocation=_body.project_id_allocation,
        user_id=_body.user_id,
        comments=_body.comment,
    )

    db.add(create_proposal_model)

    db.commit()


@router.post("/deallocation")
def create_deallocation_proposal(
    db: DbDependency, user: UserDependency, _body: CreateAllocationProposal
):
    create_proposal_model = DeallocationProposal(
        project_id_deallocation=_body.project_id_allocation,
        user_id=_body.user_id,
        reason=_body.comment,
    )

    db.add(create_proposal_model)

    db.commit()


@router.get("/allocation/{_id}")
def get_allocation_proposal_from_user(
    db: DbDependency, user: UserDependency, _id: UUID
):
    proposals = db.query(AllocationProposal).filter_by(user_id=_id).all()

    return proposals


@router.get("/deallocation/{_id}")
def get_deallocation_proposal_from_user(
    db: DbDependency, user: UserDependency, _id: UUID
):
    proposals = db.query(DeallocationProposal).filter_by(user_id=_id).all()

    return proposals


@router.post("/allocation/accept")
def accept_allocation_proposal(db: DbDependency, user: UserDependency, _id: UUID):
    proposal = db.query(AllocationProposal).filter_by(id=_id).delete()

    # WIP, same as @assign_user_to_project
    project = db.query(Projects).filter_by(id=proposal.project_id_allocation).first()
    victim_user = db.query(User).filter_by(id=proposal.user_id).first()
    project.users.append(victim_user)
    victim_user.work_hours += project.work_hours
    db.commit()


@router.post("/allocation/reject")
def reject_allocation_proposal(db: DbDependency, user: UserDependency, _id: UUID):
    db.query(AllocationProposal).filter_by(id=_id).delete()
    db.commit()


@router.post("/deallocation/accept")
def accept_deallocation_proposal(db: DbDependency, user: UserDependency, _id: UUID):
    proposal = db.query(DeallocationProposal).filter_by(id=_id).delete()

    # WIP, same as @assign_user_to_project
    project = db.query(Projects).filter_by(id=proposal.project_id_allocation).first()
    victim_user = db.query(User).filter_by(id=proposal.user_id).first()
    project.users.remove(victim_user)
    victim_user.work_hours -= project.work_hours
    db.commit()


@router.post("/deallocation/reject")
def reject_deallocation_proposal(db: DbDependency, user: UserDependency, _id: UUID):
    db.query(DeallocationProposal).filter_by(id=_id).delete()
    db.commit()
