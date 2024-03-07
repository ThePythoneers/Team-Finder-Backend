from pydantic import BaseModel


class CreateSkillModel(BaseModel):
    skill_category: list
    skill_name: str
    description: str
    author: str
    departments: list
