from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateProjectModel(BaseModel):
    project_name: str
    project_period: str
    start_date: datetime
    deadline_date: Optional[datetime] = None
    project_status: str
    technologies: list[str]
    general_description: str
    project_roles: list[str]

    # work_hours: int


class UpdateProjectModel(BaseModel):
    id: UUID
    project_name: Optional[str] = None
    project_period: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline_date: Optional[datetime] = None
    project_status: Optional[str] = None
    general_description: Optional[str] = None
    project_roles: Optional[str] = None
    work_hours: Optional[int] = None


class GetAvailableEmployeesModel(BaseModel):
    partially_available: bool
    close_to_finish: bool
    deadline: Optional[datetime] = None
    unavailable: bool


class AssignUserModel(BaseModel):
    user_id: UUID
    project_id: UUID


class AddCustomRoleToProjectModel(BaseModel):
    role_id: UUID
