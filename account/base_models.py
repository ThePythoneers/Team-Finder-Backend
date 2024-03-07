"""
BaseModels for the profile.py endpoints
"""

from pydantic import BaseModel
from uuid import UUID


class RoleRequestModel(BaseModel):
    """
    BaseModel for making set_user_role call.
    """

    user_id: str
    role_id: str


class SkillsRequestModel(BaseModel):
    user_id: UUID
    skill_id: UUID
    level: int
    experience: int
