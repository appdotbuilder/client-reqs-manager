import pytest
from app.database import reset_db
from app.services.team_member_service import (
    get_all_team_members,
    get_team_member_by_id,
    create_team_member,
    update_team_member,
    delete_team_member,
    get_team_members_with_requirement_counts,
)
from app.services.client_service import create_client
from app.services.category_service import create_category
from app.services.requirement_service import create_requirement
from app.models import TeamMemberCreate, TeamMemberUpdate, ClientCreate, CategoryCreate, RequirementCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


def test_create_team_member(new_db):
    team_member_data = TeamMemberCreate(name="Alice Smith")

    team_member = create_team_member(team_member_data)

    assert team_member is not None
    assert team_member.id is not None
    assert team_member.name == "Alice Smith"


def test_get_all_team_members_empty(new_db):
    team_members = get_all_team_members()
    assert team_members == []


def test_get_all_team_members_with_data(new_db):
    # Create test team members
    tm1_data = TeamMemberCreate(name="Charlie Brown")
    tm2_data = TeamMemberCreate(name="Alice Smith")
    tm3_data = TeamMemberCreate(name="Bob Johnson")

    create_team_member(tm1_data)
    create_team_member(tm2_data)
    create_team_member(tm3_data)

    team_members = get_all_team_members()
    assert len(team_members) == 3
    # Should be ordered by name
    names = [tm.name for tm in team_members]
    assert names == ["Alice Smith", "Bob Johnson", "Charlie Brown"]


def test_get_team_member_by_id(new_db):
    team_member_data = TeamMemberCreate(name="Alice Smith")
    created_team_member = create_team_member(team_member_data)
    assert created_team_member.id is not None

    retrieved_team_member = get_team_member_by_id(created_team_member.id)

    assert retrieved_team_member is not None
    assert retrieved_team_member.id == created_team_member.id
    assert retrieved_team_member.name == "Alice Smith"


def test_get_team_member_by_id_not_found(new_db):
    team_member = get_team_member_by_id(999)
    assert team_member is None


def test_update_team_member(new_db):
    # Create a team member
    team_member_data = TeamMemberCreate(name="Original Name")
    created_team_member = create_team_member(team_member_data)
    assert created_team_member.id is not None

    # Update the team member
    update_data = TeamMemberUpdate(name="Updated Name")
    updated_team_member = update_team_member(created_team_member.id, update_data)

    assert updated_team_member is not None
    assert updated_team_member.name == "Updated Name"
    assert updated_team_member.id == created_team_member.id


def test_update_team_member_not_found(new_db):
    update_data = TeamMemberUpdate(name="Updated Name")
    result = update_team_member(999, update_data)
    assert result is None


def test_delete_team_member_success(new_db):
    team_member_data = TeamMemberCreate(name="Alice Smith")
    created_team_member = create_team_member(team_member_data)
    assert created_team_member.id is not None

    result = delete_team_member(created_team_member.id)

    assert result is True
    assert get_team_member_by_id(created_team_member.id) is None


def test_delete_team_member_with_requirements_fails(new_db):
    # Create team member
    team_member_data = TeamMemberCreate(name="Alice Smith")
    team_member = create_team_member(team_member_data)
    assert team_member.id is not None

    # Create client and category for requirement
    client = create_client(
        ClientCreate(
            agency_name="Test Agency",
            contact_person="John Doe",
            email="john@test.com",
            phone="123",
            address="Address",
            website="https://test.com",
        )
    )
    assert client.id is not None

    category = create_category(CategoryCreate(name="Test Category"))
    assert category.id is not None

    # Create requirement assigned to team member
    req_data = RequirementCreate(
        title="Test Requirement", client_id=client.id, category_id=category.id, team_member_id=team_member.id
    )
    create_requirement(req_data)

    # Try to delete team member - should fail
    result = delete_team_member(team_member.id)
    assert result is False
    assert get_team_member_by_id(team_member.id) is not None


def test_delete_team_member_not_found(new_db):
    result = delete_team_member(999)
    assert result is False


def test_get_team_members_with_requirement_counts(new_db):
    # Create team members
    tm1 = create_team_member(TeamMemberCreate(name="Alice Smith"))
    tm2 = create_team_member(TeamMemberCreate(name="Bob Johnson"))
    create_team_member(TeamMemberCreate(name="Charlie Brown"))

    assert tm1.id is not None
    assert tm2.id is not None

    # Create client and category for requirements
    client = create_client(
        ClientCreate(
            agency_name="Test Agency",
            contact_person="John Doe",
            email="john@test.com",
            phone="123",
            address="Address",
            website="https://test.com",
        )
    )
    assert client.id is not None

    category = create_category(CategoryCreate(name="Test Category"))
    assert category.id is not None

    # Create requirements - 2 for tm1, 1 for tm2, 0 for tm3
    req1_data = RequirementCreate(
        title="Requirement 1", client_id=client.id, category_id=category.id, team_member_id=tm1.id
    )
    req2_data = RequirementCreate(
        title="Requirement 2", client_id=client.id, category_id=category.id, team_member_id=tm1.id
    )
    req3_data = RequirementCreate(
        title="Requirement 3", client_id=client.id, category_id=category.id, team_member_id=tm2.id
    )

    create_requirement(req1_data)
    create_requirement(req2_data)
    create_requirement(req3_data)

    team_members_with_counts = get_team_members_with_requirement_counts()

    assert len(team_members_with_counts) == 3

    # Find each team member in the results
    member_counts = {tm["name"]: tm["requirement_count"] for tm in team_members_with_counts}
    assert member_counts["Alice Smith"] == 2
    assert member_counts["Bob Johnson"] == 1
    assert member_counts["Charlie Brown"] == 0


def test_team_member_name_validation(new_db):
    # Create team member with valid name
    tm_data = TeamMemberCreate(name="Valid Name")
    tm = create_team_member(tm_data)
    assert tm.name == "Valid Name"


def test_team_member_update_partial_data(new_db):
    # Create team member
    team_member_data = TeamMemberCreate(name="Original Name")
    created_team_member = create_team_member(team_member_data)
    assert created_team_member.id is not None

    # Update with valid name
    update_data = TeamMemberUpdate(name="Updated Name")
    result = update_team_member(created_team_member.id, update_data)

    # Should return the updated team member
    assert result is not None
    assert result.name == "Updated Name"
