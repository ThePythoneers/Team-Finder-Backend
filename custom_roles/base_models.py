"""
BaseModels for the croles.py endpoints
"""

from pydantic import BaseModel


class CustomRole(BaseModel):
    """
    BaseModel for making create_custom_role call.
    """

    role_name: str
    organization_id: str


class GetCRolesRequest(BaseModel):
    """
    BaseModel for making get_custom_roles call.
    """

    organization_id: str
