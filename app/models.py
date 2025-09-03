from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Status(str, Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


# Persistent models (stored in database)
class Client(SQLModel, table=True):
    __tablename__ = "clients"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    agency_name: str = Field(max_length=200)
    contact_person: str = Field(max_length=100)
    email: str = Field(max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    phone: str = Field(max_length=20)
    address: str = Field(max_length=500)
    website: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    requirements: List["Requirement"] = Relationship(back_populates="client")


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    requirements: List["Requirement"] = Relationship(back_populates="category")


class TeamMember(SQLModel, table=True):
    __tablename__ = "team_members"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    requirements: List["Requirement"] = Relationship(back_populates="team_member")


class Requirement(SQLModel, table=True):
    __tablename__ = "requirements"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.TODO)
    due_date: Optional[date] = Field(default=None)
    client_id: int = Field(foreign_key="clients.id")
    category_id: int = Field(foreign_key="categories.id")
    team_member_id: Optional[int] = Field(default=None, foreign_key="team_members.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    client: Client = Relationship(back_populates="requirements")
    category: Category = Relationship(back_populates="requirements")
    team_member: Optional[TeamMember] = Relationship(back_populates="requirements")


# Non-persistent schemas (for validation, forms, API requests/responses)
class ClientCreate(SQLModel, table=False):
    agency_name: str = Field(max_length=200)
    contact_person: str = Field(max_length=100)
    email: str = Field(max_length=255)
    phone: str = Field(max_length=20)
    address: str = Field(max_length=500)
    website: str = Field(max_length=255)


class ClientUpdate(SQLModel, table=False):
    agency_name: Optional[str] = Field(default=None, max_length=200)
    contact_person: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    website: Optional[str] = Field(default=None, max_length=255)


class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)


class CategoryUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)


class TeamMemberCreate(SQLModel, table=False):
    name: str = Field(max_length=100)


class TeamMemberUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)


class RequirementCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.TODO)
    due_date: Optional[date] = Field(default=None)
    client_id: int
    category_id: int
    team_member_id: Optional[int] = Field(default=None)


class RequirementUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[Priority] = Field(default=None)
    status: Optional[Status] = Field(default=None)
    due_date: Optional[date] = Field(default=None)
    client_id: Optional[int] = Field(default=None)
    category_id: Optional[int] = Field(default=None)
    team_member_id: Optional[int] = Field(default=None)
