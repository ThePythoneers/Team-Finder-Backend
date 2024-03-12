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

    user_id: UUID
    skill_id: UUID
    level: int
    experience: int
    training_title: str
    training_description: str
    project_link: str


class DeleteSkillModel(BaseModel):
    user_id: UUID
    skill_id: UUID
