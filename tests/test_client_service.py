import pytest
from app.database import reset_db
from app.services.client_service import (
    get_all_clients,
    get_client_by_id,
    create_client,
    update_client,
    delete_client,
    get_clients_with_requirement_counts,
)
from app.services.category_service import create_category
from app.services.requirement_service import create_requirement
from app.models import ClientCreate, ClientUpdate, CategoryCreate, RequirementCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


def test_create_client(new_db):
    client_data = ClientCreate(
        agency_name="Test Agency",
        contact_person="John Doe",
        email="john@test.com",
        phone="123-456-7890",
        address="123 Test St",
        website="https://test.com",
    )

    client = create_client(client_data)

    assert client is not None
    assert client.id is not None
    assert client.agency_name == "Test Agency"
    assert client.contact_person == "John Doe"
    assert client.email == "john@test.com"


def test_get_all_clients_empty(new_db):
    clients = get_all_clients()
    assert clients == []


def test_get_all_clients_with_data(new_db):
    # Create test clients
    client1_data = ClientCreate(
        agency_name="Agency A",
        contact_person="Alice",
        email="alice@a.com",
        phone="111",
        address="Address A",
        website="https://a.com",
    )
    client2_data = ClientCreate(
        agency_name="Agency B",
        contact_person="Bob",
        email="bob@b.com",
        phone="222",
        address="Address B",
        website="https://b.com",
    )

    create_client(client1_data)
    create_client(client2_data)

    clients = get_all_clients()
    assert len(clients) == 2
    # Should be ordered by agency name
    assert clients[0].agency_name == "Agency A"
    assert clients[1].agency_name == "Agency B"


def test_get_client_by_id(new_db):
    client_data = ClientCreate(
        agency_name="Test Agency",
        contact_person="John Doe",
        email="john@test.com",
        phone="123-456-7890",
        address="123 Test St",
        website="https://test.com",
    )

    created_client = create_client(client_data)
    assert created_client.id is not None
    retrieved_client = get_client_by_id(created_client.id)

    assert retrieved_client is not None
    assert retrieved_client.id == created_client.id
    assert retrieved_client.agency_name == "Test Agency"


def test_get_client_by_id_not_found(new_db):
    client = get_client_by_id(999)
    assert client is None


def test_update_client(new_db):
    # Create a client
    client_data = ClientCreate(
        agency_name="Original Agency",
        contact_person="John Doe",
        email="john@test.com",
        phone="123-456-7890",
        address="123 Test St",
        website="https://test.com",
    )

    created_client = create_client(client_data)
    assert created_client.id is not None

    # Update the client
    update_data = ClientUpdate(agency_name="Updated Agency", contact_person="Jane Doe")

    updated_client = update_client(created_client.id, update_data)

    assert updated_client is not None
    assert updated_client.agency_name == "Updated Agency"
    assert updated_client.contact_person == "Jane Doe"
    assert updated_client.email == "john@test.com"  # Unchanged


def test_update_client_not_found(new_db):
    update_data = ClientUpdate(agency_name="Updated Agency")
    result = update_client(999, update_data)
    assert result is None


def test_delete_client_success(new_db):
    client_data = ClientCreate(
        agency_name="Test Agency",
        contact_person="John Doe",
        email="john@test.com",
        phone="123-456-7890",
        address="123 Test St",
        website="https://test.com",
    )

    created_client = create_client(client_data)
    assert created_client.id is not None
    result = delete_client(created_client.id)

    assert result is True
    assert get_client_by_id(created_client.id) is None


def test_delete_client_with_requirements_fails(new_db):
    # Create client
    client_data = ClientCreate(
        agency_name="Test Agency",
        contact_person="John Doe",
        email="john@test.com",
        phone="123-456-7890",
        address="123 Test St",
        website="https://test.com",
    )
    client = create_client(client_data)
    assert client.id is not None

    # Create category
    category = create_category(CategoryCreate(name="Test Category"))
    assert category.id is not None

    # Create requirement
    req_data = RequirementCreate(
        title="Test Requirement", description="Test", client_id=client.id, category_id=category.id
    )
    create_requirement(req_data)

    # Try to delete client - should fail
    result = delete_client(client.id)
    assert result is False
    assert get_client_by_id(client.id) is not None


def test_delete_client_not_found(new_db):
    result = delete_client(999)
    assert result is False


def test_get_clients_with_requirement_counts(new_db):
    # Create client
    client_data = ClientCreate(
        agency_name="Test Agency",
        contact_person="John Doe",
        email="john@test.com",
        phone="123-456-7890",
        address="123 Test St",
        website="https://test.com",
    )
    client = create_client(client_data)
    assert client.id is not None

    # Create category
    category = create_category(CategoryCreate(name="Test Category"))
    assert category.id is not None

    # Create requirements
    req_data1 = RequirementCreate(title="Requirement 1", client_id=client.id, category_id=category.id)
    req_data2 = RequirementCreate(title="Requirement 2", client_id=client.id, category_id=category.id)
    create_requirement(req_data1)
    create_requirement(req_data2)

    clients_with_counts = get_clients_with_requirement_counts()

    assert len(clients_with_counts) == 1
    client_info = clients_with_counts[0]
    assert client_info["agency_name"] == "Test Agency"
    assert client_info["requirement_count"] == 2


def test_client_data_validation(new_db):
    # Test with all required fields - should work
    client_data = ClientCreate(
        agency_name="Test Agency",
        contact_person="John Doe",
        email="john@test.com",
        phone="123",
        address="Address",
        website="https://test.com",
    )
    client = create_client(client_data)
    assert client.agency_name == "Test Agency"
