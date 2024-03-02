"""
BaseModels for the profile.py endpoints
"""

from pydantic import BaseModel


class RoleRequestModel(BaseModel):
    """
    BaseModel for making set_user_role call.
    """

    user_id: str
    role_id: str
