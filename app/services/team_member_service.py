from typing import List, Optional
from sqlmodel import select
from app.database import get_session
from app.models import TeamMember, TeamMemberCreate, TeamMemberUpdate


def get_all_team_members() -> List[TeamMember]:
    """Get all team members ordered by name."""
    with get_session() as session:
        statement = select(TeamMember).order_by(TeamMember.name)
        return list(session.exec(statement))


def get_team_member_by_id(team_member_id: int) -> Optional[TeamMember]:
    """Get a team member by ID."""
    with get_session() as session:
        return session.get(TeamMember, team_member_id)


def create_team_member(team_member_data: TeamMemberCreate) -> TeamMember:
    """Create a new team member."""
    with get_session() as session:
        team_member = TeamMember(**team_member_data.model_dump())
        session.add(team_member)
        session.commit()
        session.refresh(team_member)
        return team_member


def update_team_member(team_member_id: int, team_member_data: TeamMemberUpdate) -> Optional[TeamMember]:
    """Update an existing team member."""
    with get_session() as session:
        team_member = session.get(TeamMember, team_member_id)
        if team_member is None:
            return None

        update_data = team_member_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(team_member, field, value)

        session.add(team_member)
        session.commit()
        session.refresh(team_member)
        return team_member


def delete_team_member(team_member_id: int) -> bool:
    """Delete a team member if they have no assigned requirements."""
    with get_session() as session:
        team_member = session.get(TeamMember, team_member_id)
        if team_member is None:
            return False

        # Check if team member has requirements
        if team_member.requirements:
            return False

        session.delete(team_member)
        session.commit()
        return True


def get_team_members_with_requirement_counts() -> List[dict]:
    """Get all team members with their requirement counts."""
    with get_session() as session:
        team_members = session.exec(select(TeamMember).order_by(TeamMember.name)).all()
        return [
            {
                "id": team_member.id,
                "name": team_member.name,
                "requirement_count": len(team_member.requirements) if team_member.requirements else 0,
            }
            for team_member in team_members
        ]
