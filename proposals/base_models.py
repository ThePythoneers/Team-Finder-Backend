from uuid import UUID

from pydantic import BaseModel


class CreateAllocationProposal(BaseModel):
    project_id_allocation: UUID
    user_id: UUID
    comment: str
