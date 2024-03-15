from uuid import UUID
from pydantic import BaseModel


class CreateTStackModel(BaseModel):
    technology_name: str


class AssignTStackModel(BaseModel):
    project_id: UUID
    tech_id: UUID
