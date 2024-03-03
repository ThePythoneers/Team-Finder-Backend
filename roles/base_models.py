from pydantic import BaseModel


class ModifyRoleModel(BaseModel):
    user_id: str
    role_name: str
