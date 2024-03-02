"""
BaseModels for the authentication.py endpoints
"""

from pydantic import BaseModel


class RegisterOwner(BaseModel):
    """
    BaseModel for making create_user_employee call.
    """

    username: str
    email: str
    password: str
    organization_name: str
    hq_address: str


class RegisterEmployee(BaseModel):
    """
    BaseModel for making create_user call.
    """

    username: str
    email: str
    password: str


class Token(BaseModel):
    """
    BaseModel for making token call.
    """

    access_token: str
    token_type: str
    user: dict
