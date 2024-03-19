from pydantic import BaseModel
from uuid import UUID


class GetChatGPTInfo(BaseModel):
    message: str
    project_id: UUID
