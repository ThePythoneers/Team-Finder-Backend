from pydantic import BaseModel

class Users(BaseModel):
    username: str
    type_: str
    email: str
    password: str
    organization_name: str
    hq_address: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict