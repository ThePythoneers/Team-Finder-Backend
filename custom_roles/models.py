from pydantic import BaseModel

class CustomRole(BaseModel):
    role_name: str
    organization_id: str

class GetCRolesRequest(BaseModel):
    organization_id: str