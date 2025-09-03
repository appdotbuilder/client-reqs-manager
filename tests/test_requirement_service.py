import pytest
from datetime import date
from app.database import reset_db
from app.services.requirement_service import (
    get_all_requirements,
    get_requirement_by_id,
    create_requirement,
    update_requirement,
    delete_requirement,
    get_requirements_by_client,
    get_requirements_by_team_member,
    get_requirements_summary,
)
from app.services.client_service import create_client
from app.services.category_service import create_category
from app.services.team_member_service import create_team_member
from app.models import (
    RequirementCreate,
    RequirementUpdate,
    ClientCreate,
    CategoryCreate,
    TeamMemberCreate,
    Priority,
    Status,
)


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


@pytest.fixture()
def test_data(new_db):
    # Create test client
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

    # Create test category
    category = create_category(CategoryCreate(name="Test Category"))

    # Create test team member
    team_member = create_team_member(TeamMemberCreate(name="Alice"))

    return {"client": client, "category": category, "team_member": team_member}


def test_create_requirement_basic(test_data):
    req_data = RequirementCreate(
        title="Test Requirement",
        description="Test description",
        client_id=test_data["client"].id,
        category_id=test_data["category"].id,
    )

    requirement = create_requirement(req_data)

    assert requirement is not None
    assert requirement.id is not None
    assert requirement.title == "Test Requirement"
    assert requirement.description == "Test description"
    assert requirement.priority == Priority.MEDIUM  # default
    assert requirement.status == Status.TODO  # default
    assert requirement.client_id == test_data["client"].id
    assert requirement.category_id == test_data["category"].id
    assert requirement.team_member_id is None


def test_create_requirement_with_all_fields(test_data):
    due_date = date(2024, 12, 31)
    req_data = RequirementCreate(
        title="Complete Requirement",
        description="Detailed description",
        priority=Priority.HIGH,
        status=Status.IN_PROGRESS,
        due_date=due_date,
        client_id=test_data["client"].id,
        category_id=test_data["category"].id,
        team_member_id=test_data["team_member"].id,
    )

    requirement = create_requirement(req_data)

    assert requirement is not None
    assert requirement.title == "Complete Requirement"
    assert requirement.priority == Priority.HIGH
    assert requirement.status == Status.IN_PROGRESS
    assert requirement.due_date == due_date
    assert requirement.team_member_id == test_data["team_member"].id


def test_create_requirement_invalid_client(test_data):
    req_data = RequirementCreate(
        title="Test Requirement",
        client_id=999,  # Non-existent client
        category_id=test_data["category"].id,
    )

    result = create_requirement(req_data)
    assert result is None


def test_create_requirement_invalid_category(test_data):
    req_data = RequirementCreate(
        title="Test Requirement",
        client_id=test_data["client"].id,
        category_id=999,  # Non-existent category
    )

    result = create_requirement(req_data)
    assert result is None


def test_create_requirement_invalid_team_member(test_data):
    req_data = RequirementCreate(
        title="Test Requirement",
        client_id=test_data["client"].id,
        category_id=test_data["category"].id,
        team_member_id=999,  # Non-existent team member
    )

    result = create_requirement(req_data)
    assert result is None


def test_get_all_requirements_empty(new_db):
    requirements = get_all_requirements()
    assert requirements == []


def test_get_all_requirements_with_data(test_data):
    # Create multiple requirements
    req1_data = RequirementCreate(
        title="Requirement 1", client_id=test_data["client"].id, category_id=test_data["category"].id
    )
    req2_data = RequirementCreate(
        title="Requirement 2",
        priority=Priority.HIGH,
        client_id=test_data["client"].id,
        category_id=test_data["category"].id,
    )

    create_requirement(req1_data)
    create_requirement(req2_data)

    requirements = get_all_requirements()
    assert len(requirements) == 2
    # Should be ordered by created_at desc (newest first)
    assert requirements[0].title == "Requirement 2"
    assert requirements[1].title == "Requirement 1"


def test_get_requirement_by_id(test_data):
    req_data = RequirementCreate(
        title="Test Requirement", client_id=test_data["client"].id, category_id=test_data["category"].id
    )

    created_req = create_requirement(req_data)
    assert created_req is not None and created_req.id is not None
    retrieved_req = get_requirement_by_id(created_req.id)

    assert retrieved_req is not None
    assert retrieved_req.id == created_req.id
    assert retrieved_req.title == "Test Requirement"
    # Verify relationships are loaded
    assert retrieved_req.client.agency_name == test_data["client"].agency_name
    assert retrieved_req.category.name == test_data["category"].name


def test_get_requirement_by_id_not_found(new_db):
    requirement = get_requirement_by_id(999)
    assert requirement is None


def test_update_requirement(test_data):
    # Create requirement
    req_data = RequirementCreate(
        title="Original Title", client_id=test_data["client"].id, category_id=test_data["category"].id
    )
    created_req = create_requirement(req_data)
    assert created_req is not None and created_req.id is not None

    # Update requirement
    update_data = RequirementUpdate(
        title="Updated Title", status=Status.DONE, team_member_id=test_data["team_member"].id
    )

    updated_req = update_requirement(created_req.id, update_data)

    assert updated_req is not None
    assert updated_req.title == "Updated Title"
    assert updated_req.status == Status.DONE
    assert updated_req.team_member_id == test_data["team_member"].id
    assert updated_req.priority == Priority.MEDIUM  # Unchanged
    assert updated_req.updated_at > updated_req.created_at


def test_update_requirement_not_found(new_db):
    update_data = RequirementUpdate(title="Updated Title")
    result = update_requirement(999, update_data)
    assert result is None


def test_update_requirement_invalid_references(test_data):
    # Create requirement
    req_data = RequirementCreate(
        title="Test Requirement", client_id=test_data["client"].id, category_id=test_data["category"].id
    )
    created_req = create_requirement(req_data)
    assert created_req is not None and created_req.id is not None

    # Try to update with invalid client
    update_data = RequirementUpdate(client_id=999)
    result = update_requirement(created_req.id, update_data)
    assert result is None

    # Try to update with invalid category
    update_data = RequirementUpdate(category_id=999)
    result = update_requirement(created_req.id, update_data)
    assert result is None

    # Try to update with invalid team member
    update_data = RequirementUpdate(team_member_id=999)
    result = update_requirement(created_req.id, update_data)
    assert result is None


def test_delete_requirement(test_data):
    req_data = RequirementCreate(
        title="Test Requirement", client_id=test_data["client"].id, category_id=test_data["category"].id
    )
    created_req = create_requirement(req_data)
    assert created_req is not None and created_req.id is not None

    result = delete_requirement(created_req.id)
    assert result is True
    assert get_requirement_by_id(created_req.id) is None


def test_delete_requirement_not_found(new_db):
    result = delete_requirement(999)
    assert result is False


def test_get_requirements_by_client(test_data):
    # Create requirements for the client
    req1_data = RequirementCreate(
        title="Requirement 1", client_id=test_data["client"].id, category_id=test_data["category"].id
    )
    req2_data = RequirementCreate(
        title="Requirement 2", client_id=test_data["client"].id, category_id=test_data["category"].id
    )

    # Create another client and requirement
    other_client = create_client(
        ClientCreate(
            agency_name="Other Agency",
            contact_person="Jane",
            email="jane@other.com",
            phone="456",
            address="Other Address",
            website="https://other.com",
        )
    )
    assert other_client.id is not None
    req3_data = RequirementCreate(
        title="Other Requirement", client_id=other_client.id, category_id=test_data["category"].id
    )

    create_requirement(req1_data)
    create_requirement(req2_data)
    create_requirement(req3_data)

    assert test_data["client"].id is not None
    client_requirements = get_requirements_by_client(test_data["client"].id)

    assert len(client_requirements) == 2
    titles = [req.title for req in client_requirements]
    assert "Requirement 1" in titles
    assert "Requirement 2" in titles
    assert "Other Requirement" not in titles


def test_get_requirements_by_team_member(test_data):
    # Create team member requirements
    req1_data = RequirementCreate(
        title="Assigned Requirement 1",
        client_id=test_data["client"].id,
        category_id=test_data["category"].id,
        team_member_id=test_data["team_member"].id,
    )
    req2_data = RequirementCreate(
        title="Assigned Requirement 2",
        client_id=test_data["client"].id,
        category_id=test_data["category"].id,
        team_member_id=test_data["team_member"].id,
    )

    # Create unassigned requirement
    req3_data = RequirementCreate(
        title="Unassigned Requirement", client_id=test_data["client"].id, category_id=test_data["category"].id
    )

    create_requirement(req1_data)
    create_requirement(req2_data)
    create_requirement(req3_data)

    assert test_data["team_member"].id is not None
    team_requirements = get_requirements_by_team_member(test_data["team_member"].id)

    assert len(team_requirements) == 2
    titles = [req.title for req in team_requirements]
    assert "Assigned Requirement 1" in titles
    assert "Assigned Requirement 2" in titles
    assert "Unassigned Requirement" not in titles


def test_get_requirements_summary(test_data):
    # Create requirements with different statuses and priorities
    yesterday = date.today().replace(day=date.today().day - 1)

    req1_data = RequirementCreate(
        title="High Priority Todo",
        priority=Priority.HIGH,
        status=Status.TODO,
        due_date=yesterday,  # Overdue
        client_id=test_data["client"].id,
        category_id=test_data["category"].id,
    )
    req2_data = RequirementCreate(
        title="Medium Priority In Progress",
        priority=Priority.MEDIUM,
        status=Status.IN_PROGRESS,
        client_id=test_data["client"].id,
        category_id=test_data["category"].id,
    )
    req3_data = RequirementCreate(
        title="Low Priority Done",
        priority=Priority.LOW,
        status=Status.DONE,
        due_date=yesterday,  # Not overdue because done
        client_id=test_data["client"].id,
        category_id=test_data["category"].id,
    )

    create_requirement(req1_data)
    create_requirement(req2_data)
    create_requirement(req3_data)

    summary = get_requirements_summary()

    assert summary["total"] == 3
    assert summary["by_status"]["To Do"] == 1
    assert summary["by_status"]["In Progress"] == 1
    assert summary["by_status"]["Done"] == 1
    assert summary["by_priority"]["High"] == 1
    assert summary["by_priority"]["Medium"] == 1
    assert summary["by_priority"]["Low"] == 1
    assert summary["overdue"] == 1  # Only the todo with past due date
