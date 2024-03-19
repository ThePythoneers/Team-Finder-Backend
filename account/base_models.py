"""
BaseModels for the profile.py endpoints
"""

from uuid import UUID

from pydantic import BaseModel


class RoleRequestModel(BaseModel):
    """
    BaseModel for making set_user_role call.
    """

    user_id: str
    role_id: str


class SkillsRequestModel(BaseModel):
    """
    BaseModel
    """

    skill_id: UUID
    level: int
    experience: int
    training_title: str = None
    training_description: str = None
    project_link: UUID = None


class DeleteSkillModel(BaseModel):
    skill_id: UUID
