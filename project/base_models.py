from typing import Optional
from datetime import date
from uuid import UUID

from pydantic import BaseModel


class CreateProjectModel(BaseModel):
    project_name: str
    project_period: str
    start_date: date
    deadline_date: Optional[date] = None
    project_status: str
    general_description: str
    work_hours: int


class UpdateProjectModel(BaseModel):
    id: UUID
    project_name: str
    project_period: str
    start_date: date
    deadline_date: Optional[date] = None
    project_status: str
    description: str
    work_hours: int


class GetAvailableEmployeesModel(BaseModel):
    partially_available: bool
    close_to_finish: bool
    deadline: Optional[int] = None
    unavailable: bool


class AssignUserModel(BaseModel):
    user_id: UUID
    project_id: UUID


class AddCustomRoleToProjectModel(BaseModel):
    role_id: UUID
