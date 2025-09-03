from typing import List, Optional
from datetime import datetime
from sqlmodel import select, desc
from app.database import get_session
from app.models import Requirement, RequirementCreate, RequirementUpdate, Client, Category, TeamMember, Status


def get_all_requirements() -> List[Requirement]:
    """Get all requirements with related data loaded."""
    with get_session() as session:
        statement = select(Requirement).order_by(desc(Requirement.created_at))
        requirements = session.exec(statement).all()

        # Explicitly load relationships to avoid lazy loading issues
        for req in requirements:
            _ = req.client.agency_name  # Force load client
            _ = req.category.name  # Force load category
            if req.team_member:
                _ = req.team_member.name  # Force load team member

        return list(requirements)


def get_requirement_by_id(requirement_id: int) -> Optional[Requirement]:
    """Get a requirement by ID with relationships loaded."""
    with get_session() as session:
        req = session.get(Requirement, requirement_id)
        if req:
            # Force load relationships
            _ = req.client.agency_name
            _ = req.category.name
            if req.team_member:
                _ = req.team_member.name
        return req


def create_requirement(requirement_data: RequirementCreate) -> Optional[Requirement]:
    """Create a new requirement."""
    with get_session() as session:
        # Validate client exists
        client = session.get(Client, requirement_data.client_id)
        if client is None:
            return None

        # Validate category exists
        category = session.get(Category, requirement_data.category_id)
        if category is None:
            return None

        # Validate team member exists if provided
        if requirement_data.team_member_id is not None:
            team_member = session.get(TeamMember, requirement_data.team_member_id)
            if team_member is None:
                return None

        requirement = Requirement(**requirement_data.model_dump())
        session.add(requirement)
        session.commit()
        session.refresh(requirement)

        # Load relationships
        _ = requirement.client.agency_name
        _ = requirement.category.name
        if requirement.team_member:
            _ = requirement.team_member.name

        return requirement


def update_requirement(requirement_id: int, requirement_data: RequirementUpdate) -> Optional[Requirement]:
    """Update an existing requirement."""
    with get_session() as session:
        requirement = session.get(Requirement, requirement_id)
        if requirement is None:
            return None

        update_data = requirement_data.model_dump(exclude_unset=True)

        # Validate references if they're being updated
        if "client_id" in update_data:
            client = session.get(Client, update_data["client_id"])
            if client is None:
                return None

        if "category_id" in update_data:
            category = session.get(Category, update_data["category_id"])
            if category is None:
                return None

        if "team_member_id" in update_data and update_data["team_member_id"] is not None:
            team_member = session.get(TeamMember, update_data["team_member_id"])
            if team_member is None:
                return None

        for field, value in update_data.items():
            setattr(requirement, field, value)

        requirement.updated_at = datetime.utcnow()
        session.add(requirement)
        session.commit()
        session.refresh(requirement)

        # Load relationships
        _ = requirement.client.agency_name
        _ = requirement.category.name
        if requirement.team_member:
            _ = requirement.team_member.name

        return requirement


def delete_requirement(requirement_id: int) -> bool:
    """Delete a requirement."""
    with get_session() as session:
        requirement = session.get(Requirement, requirement_id)
        if requirement is None:
            return False

        session.delete(requirement)
        session.commit()
        return True


def get_requirements_by_client(client_id: int) -> List[Requirement]:
    """Get all requirements for a specific client."""
    with get_session() as session:
        statement = select(Requirement).where(Requirement.client_id == client_id).order_by(desc(Requirement.created_at))
        requirements = session.exec(statement).all()

        # Load relationships
        for req in requirements:
            _ = req.client.agency_name
            _ = req.category.name
            if req.team_member:
                _ = req.team_member.name

        return list(requirements)


def get_requirements_by_team_member(team_member_id: int) -> List[Requirement]:
    """Get all requirements assigned to a specific team member."""
    with get_session() as session:
        statement = (
            select(Requirement)
            .where(Requirement.team_member_id == team_member_id)
            .order_by(desc(Requirement.created_at))
        )
        requirements = session.exec(statement).all()

        # Load relationships
        for req in requirements:
            _ = req.client.agency_name
            _ = req.category.name
            if req.team_member:
                _ = req.team_member.name

        return list(requirements)


def get_requirements_summary() -> dict:
    """Get summary statistics for requirements."""
    with get_session() as session:
        all_requirements = session.exec(select(Requirement)).all()

        total = len(all_requirements)
        by_status = {}
        by_priority = {}
        overdue = 0

        from datetime import date

        today = date.today()

        for req in all_requirements:
            # Count by status
            status_str = req.status.value
            by_status[status_str] = by_status.get(status_str, 0) + 1

            # Count by priority
            priority_str = req.priority.value
            by_priority[priority_str] = by_priority.get(priority_str, 0) + 1

            # Count overdue
            if req.due_date and req.due_date < today and req.status != Status.DONE:
                overdue += 1

        return {"total": total, "by_status": by_status, "by_priority": by_priority, "overdue": overdue}
