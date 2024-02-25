from pydantic import BaseModel

class RoleRequestModel(BaseModel):
    user_id: str
    roles: list