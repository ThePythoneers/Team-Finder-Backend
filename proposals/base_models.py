from uuid import UUID

from pydantic import BaseModel


class CreateAllocationProposal(BaseModel):
    user_id: UUID
    comment: str
    work_hours: int
    roles: list[UUID]
    project_id: UUID


class CreateDeallocationProposal(BaseModel):
    user_id: UUID
    comment: str
    project_id: UUID
