from pydantic import BaseModel
from uuid import UUID


class CreateSkillModel(BaseModel):
    skill_category: list[UUID]
    skill_name: str
    description: str
