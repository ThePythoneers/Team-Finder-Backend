from pydantic import BaseModel
from uuid import UUID

class RoleRequestModel(BaseModel):
    user_id: str
    role_id: str