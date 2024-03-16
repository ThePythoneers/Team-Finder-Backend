from uuid import UUID

from pydantic import BaseModel


class CreateAllocationProposal(BaseModel):
    project_id_allocation: UUID
    user_id: UUID
    work_hours: int
    team_roles: list[UUID]
    comments: str

class CreateDeAllocationProposal(BaseModel):
    project_id_allocation: UUID
    user_id: UUID
    comments: str
