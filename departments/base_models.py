from pydantic import BaseModel
from uuid import UUID


class CreateDepartmentModel(BaseModel):
    department_name: str


class DeleteDepartmentModel(BaseModel):
    department_id: UUID


class AssignManagerModel(BaseModel):
    department_id: UUID
    manager_id: UUID


class DeleteManagerModel(BaseModel):
    department_id: UUID


class AddUserToDepartmentModel(BaseModel):
    user_id: UUID
