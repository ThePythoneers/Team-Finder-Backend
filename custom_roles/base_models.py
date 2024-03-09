"""
BaseModels for the croles.py endpoints
"""

from uuid import UUID

from pydantic import BaseModel


class CreateCustomRoleModel(BaseModel):
    project_id: UUID
    role_name: str


class AssignCustomRoleModel(BaseModel):
    project_id: UUID
    role_id: UUID
    user_id: UUID
