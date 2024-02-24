from pydantic import BaseModel


class OrganizationOwner(BaseModel):
    username: str
    email: str
    password: str
    organization_name: str
    hq_address: str

class Employee(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str