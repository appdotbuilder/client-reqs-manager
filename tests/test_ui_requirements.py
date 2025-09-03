import pytest
from nicegui.testing import User
from app.database import reset_db
from app.services.client_service import create_client
from app.services.category_service import create_category
from app.services.team_member_service import create_team_member
from app.models import ClientCreate, CategoryCreate, TeamMemberCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


@pytest.fixture()
def test_data(new_db):
    # Create test data for UI tests
    client = create_client(
        ClientCreate(
            agency_name="Test Agency",
            contact_person="John Doe",
            email="john@test.com",
            phone="123-456-7890",
            address="123 Test St",
            website="https://test.com",
        )
    )

    category = create_category(CategoryCreate(name="Web Development"))
    team_member = create_team_member(TeamMemberCreate(name="Alice Smith"))

    return {"client": client, "category": category, "team_member": team_member}


async def test_dashboard_loads(user: User, new_db) -> None:
    await user.open("/dashboard")
    await user.should_see("Dashboard Overview")
    await user.should_see("Total Requirements")
    await user.should_see("Active Clients")
    await user.should_see("Navigation")


async def test_dashboard_navigation(user: User, new_db) -> None:
    await user.open("/dashboard")

    # Test navigation to clients
    user.find("Clients").click()
    await user.should_see("Client Management")

    # Navigate back to dashboard
    user.find("← Back to Dashboard").click()
    await user.should_see("Dashboard Overview")

    # Test navigation to requirements
    user.find("Requirements").click()
    await user.should_see("Requirements Management")


async def test_clients_page_empty_state(user: User, new_db) -> None:
    await user.open("/clients")
    await user.should_see("Client Management")
    await user.should_see("No clients found")
    await user.should_see("Add your first client to get started")


async def test_requirements_page_empty_state(user: User, new_db) -> None:
    await user.open("/requirements")
    await user.should_see("Requirements Management")
    await user.should_see("No requirements found")
    await user.should_see("Add your first requirement to get started")


async def test_settings_page_loads(user: User, new_db) -> None:
    await user.open("/settings")
    await user.should_see("Application Settings")
    await user.should_see("Categories")
    await user.should_see("Team Members")
    await user.should_see("No categories found")
    await user.should_see("No team members found")


async def test_client_creation_flow(user: User, new_db) -> None:
    await user.open("/clients")

    # Click add new client
    user.find("Add New Client").click()
    await user.should_see("Add New Client")

    # For now, just verify form opened correctly
    await user.should_see("Agency Name")
    await user.should_see("Contact Person")

    # Just verify Save button is present
    await user.should_see("Save")


async def test_category_creation_flow(user: User, new_db) -> None:
    await user.open("/settings")

    # Click add category
    user.find("Add Category").click()
    await user.should_see("Add New Category")

    # Verify form opened
    await user.should_see("Category Name")

    # Just verify Save button is present
    await user.should_see("Save")


async def test_team_member_creation_flow(user: User, new_db) -> None:
    await user.open("/settings")

    # Click add team member
    user.find("Add Team Member").click()
    await user.should_see("Add New Team Member")

    # Verify form opened
    await user.should_see("Team Member Name")

    # Just verify Save button is present
    await user.should_see("Save")


async def test_requirement_creation_flow(user: User, test_data) -> None:
    await user.open("/requirements")

    # Click add new requirement
    user.find("Add New Requirement").click()
    await user.should_see("Add New Requirement")

    # Verify form fields are present
    await user.should_see("Title")
    await user.should_see("Description")

    # Select client (should be available from test_data)
    # Note: In a real test, we'd need to interact with the select dropdown
    # For now, we just verify the form opens correctly
    await user.should_see("Client")
    await user.should_see("Category")
    await user.should_see("Priority")
    await user.should_see("Status")


async def test_root_redirect(user: User, new_db) -> None:
    """Test that root URL redirects to dashboard"""
    await user.open("/")
    await user.should_see("Dashboard Overview")
