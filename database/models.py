"""
Base of all the database. Here are all tables that this server uses.
"""

from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import (
    ARRAY,
    ForeignKey,
    Table,
    Column,
    UUID,
    String,
    INTEGER,
    DATE,
    UniqueConstraint,
)
from sqlalchemy import DateTime


# pylint: disable=missing-class-docstring,too-few-public-methods
class Base(DeclarativeBase):
    pass


users_primary_roles = Table(
    "users_primary_roles",
    Base.metadata,
    Column("primary_role_id", ForeignKey("primary_roles.id")),
    Column("user_id", ForeignKey("users.id")),
)
departments_skills = Table(
    "departments_skills",
    Base.metadata,
    Column("department_id", ForeignKey("departments.id")),
    Column("skill_id", ForeignKey("skills.id")),
)
project_custom_roles = Table(
    "project_custom_roles",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id")),
    Column("custom_role_id", ForeignKey("custom_roles.id")),
    Column("project_members", INTEGER),
)

user_skills = Table(
    "user_skills",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("skill_id", ForeignKey("skills.id")),
    Column(
        "skill_level", INTEGER
    ),  # 1 - Learns 2 - Knows 3 - Does 4 - Helps 5 - Teaches
    Column(
        "skill_experience", INTEGER
    ),  # 0-6 months 6-12 months 1-2 years 2-4 years 4-7 years > 7 years
)

user_projects = Table(
    "user_projects",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("project_id", ForeignKey("projects.id")),
)

dealloc_user_projects = Table(
    "dealloc_user_projects",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("project_id", ForeignKey("projects.id")),
)


# la custom roles nu sunt sigur cum functioneaza
# Mergem pe cea de jos ca asa am gasit pe net si vedem ce face


# pylint: disable=invalid-name
class User_Skills(Base):
    __tablename__ = "users_skills"
    id = Column(UUID, default=uuid4, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    skill_id = Column(UUID, ForeignKey("skills.id"))
    skill_level = Column(INTEGER)
    skill_experience = Column(INTEGER)
    training_title = Column(String)
    training_description = Column(String)

    user = relationship("User", back_populates="skill_level")


# pylint: disable=invalid-name
class Users_Custom_Roles(Base):
    __tablename__ = "users_custom_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), primary_key=True)
    custom_role_id = Column(
        UUID(as_uuid=True), ForeignKey("custom_roles.id"), primary_key=True
    )
    UniqueConstraint("user_id", "project_id", "custom_role_id")
    relationship("User", back_populates="memberships", lazy="dynamic")
    relationship("Project", back_populates="memberships", lazy="dynamic")
    relationship("Custom_Role", back_populates="memberships", lazy="dynamic")


# pylint: disable=invalid-name
class Department_projects(Base):
    __tablename__ = "department_projects"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), primary_key=True)
    department_id = Column(
        UUID(as_uuid=True), ForeignKey("departments.id"), primary_key=True
    )
    UniqueConstraint("user_id", "project_id", "department_id")
    relationship("User", back_populates="department_projects", lazy="dynamic")
    relationship("Project", back_populates="department_projects", lazy="dynamic")
    relationship("Department", back_populates="department_projects", lazy="dynamic")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="employees")
    department_id = Column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )
    department = relationship("Department", back_populates="department_users")
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    # organization
    primary_roles = relationship(
        "Primary_Roles", secondary=users_primary_roles, back_populates="users"
    )
    skill_level = relationship("User_Skills", back_populates="user")
    # department
    projects = relationship("Projects", secondary=user_projects, back_populates="users")
    work_hours = Column(INTEGER)


# pylint: disable=invalid-name
class Primary_Roles(Base):
    __tablename__ = "primary_roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    role_name = Column(String, nullable=False)  # admin d_manager p_manager
    users = relationship(
        "User", secondary=users_primary_roles, back_populates="primary_roles"
    )


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    organization_name = Column(String, nullable=False)
    hq_address = Column(String, nullable=False)
    custom_link = Column(String, nullable=False)
    owner_id = Column(
        UUID(as_uuid=True), nullable=False
    )  # nu cred ca avem nevoie de relationship
    employees = relationship("User", back_populates="organization")
    created_at = Column(DateTime, default=datetime.now, nullable=False)


class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    department_name = Column(String, nullable=False)
    department_manager = Column(UUID(as_uuid=True))
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    department_users = relationship("User", back_populates="department")
    skills = relationship(
        "Skill", secondary=departments_skills, back_populates="departments"
    )
    created_at = Column(DateTime, default=datetime.now, nullable=False)


# skills_categories = Table(
#     "skills_categories",
#     Base.metadata,
#     Column("skill_id", ForeignKey("skills.id")),
#     Column("skill_category_id", ForeignKey("skill_categories.id")),
# )


# pylint: disable=invalid-name
class Skill_Category(Base):
    __tablename__ = "skill_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    category_name = Column(String, nullable=False)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    skill_category = Column(ARRAY(UUID))
    skill_name = Column(String, nullable=False)
    skill_description = Column(String, nullable=False)
    organization_id = Column(UUID, ForeignKey("organizations.id"))
    author = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    departments = relationship(
        "Department", secondary=departments_skills, back_populates="skills"
    )
    user_level = relationship("User_Skills")


# pylint: disable=invalid-name
class Custom_Roles(Base):
    __tablename__ = "custom_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    custom_role_name = Column(String, nullable=False)
    organization_id = Column(String)
    projects = relationship(
        "Projects", secondary=project_custom_roles, back_populates="project_roles"
    )


class Projects(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    project_name = Column(String, nullable=False)
    project_period = Column(String, nullable=False)  # Fixed, Ongoing
    start_date = Column(DATE, nullable=False)
    deadline_date = Column(DATE, nullable=True)
    project_status = Column(
        String, nullable=False
    )  # Not started | Starting | In Progress | Closing | Closed
    description = Column(String, nullable=False)
    technology_stack = Column(String)  # idk
    project_roles = relationship(
        "Custom_Roles", secondary=project_custom_roles, back_populates="projects"
    )
    users = relationship("User", secondary=user_projects, back_populates="projects")
    deallocated_users = relationship(
        "User", secondary=dealloc_user_projects, backref="past_projects"
    )
    work_hours = Column(INTEGER, nullable=False)


class AllocationProposal(Base):
    __tablename__ = "allocation_proposals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    project_id_allocation = Column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    comments = Column(String)


class DeallocationProposal(Base):
    __tablename__ = "deallocation_proposals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    project_id_deallocation = Column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason = Column(String)
