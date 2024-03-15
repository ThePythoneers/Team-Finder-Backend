from pydantic import BaseModel
from uuid import UUID


class CreateSkillModel(BaseModel):
    skill_category: list[UUID]
    skill_name: str
    description: str


class EditSkillCategoryModel(BaseModel):
    category_name: str
    category_id: UUID
