from uuid import UUID

from pydantic import BaseModel


class CreateAllocationProposal(BaseModel):
    user_id: UUID
    comment: str
    work_hours: int
    roles: list[UUID]

class CreateDeallocationProposal(BaseModel):
    project_id: UUID
    user_id: UUID
    comment: str
