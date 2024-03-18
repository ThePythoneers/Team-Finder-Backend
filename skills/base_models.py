from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class CreateSkillModel(BaseModel):
    skill_category: list[UUID]
    skill_name: str
    description: str
    department_id: Optional[UUID]


class EditSkillCategoryModel(BaseModel):
    category_name: str
    category_id: UUID
