from typing import Optional
from datetime import date
from uuid import UUID

from pydantic import BaseModel


class CreateProjectModel(BaseModel):
    project_name: str
    project_period: str
    start_date: date
    deadline_date: Optional[date]
    project_status: str
    general_description: str
    technology_stack: list
    team_roles: list


class UpdateProjectModel(BaseModel):
    project_id: UUID
    project_name: Optional[str] = None
    project_period: Optional[str] = None
    start_date: Optional[date] = None
    deadline_date: Optional[date] = None
    project_status: Optional[str] = None
    general_description: Optional[str] = None
    technology_stack: Optional[str] = None
    team_roles: Optional[str] = None


class GetAvailableEmployeesModel(BaseModel):
    partially_available: bool
    close_to_finish: bool
    deadline: Optional[int] = None
    unavailable: bool


class AssignUserModel(BaseModel):
    user_id: str
    project_id: str
