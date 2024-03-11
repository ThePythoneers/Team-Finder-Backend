from pydantic import BaseModel

class GetChatGPTInfo(BaseModel):
    message: str
