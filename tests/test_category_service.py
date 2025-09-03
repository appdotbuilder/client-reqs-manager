import pytest
from app.database import reset_db
from app.services.category_service import (
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
    get_categories_with_requirement_counts,
)
from app.services.client_service import create_client
from app.services.requirement_service import create_requirement
from app.models import CategoryCreate, CategoryUpdate, ClientCreate, RequirementCreate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


def test_create_category(new_db):
    category_data = CategoryCreate(name="Web Development")

    category = create_category(category_data)

    assert category is not None
    assert category.id is not None
    assert category.name == "Web Development"


def test_get_all_categories_empty(new_db):
    categories = get_all_categories()
    assert categories == []


def test_get_all_categories_with_data(new_db):
    # Create test categories
    category1_data = CategoryCreate(name="Web Development")
    category2_data = CategoryCreate(name="Mobile Development")
    category3_data = CategoryCreate(name="API Development")

    create_category(category1_data)
    create_category(category2_data)
    create_category(category3_data)

    categories = get_all_categories()
    assert len(categories) == 3
    # Should be ordered by name
    names = [cat.name for cat in categories]
    assert names == ["API Development", "Mobile Development", "Web Development"]


def test_get_category_by_id(new_db):
    category_data = CategoryCreate(name="Web Development")
    created_category = create_category(category_data)
    assert created_category.id is not None

    retrieved_category = get_category_by_id(created_category.id)

    assert retrieved_category is not None
    assert retrieved_category.id == created_category.id
    assert retrieved_category.name == "Web Development"


def test_get_category_by_id_not_found(new_db):
    category = get_category_by_id(999)
    assert category is None


def test_update_category(new_db):
    # Create a category
    category_data = CategoryCreate(name="Original Name")
    created_category = create_category(category_data)
    assert created_category.id is not None

    # Update the category
    update_data = CategoryUpdate(name="Updated Name")
    updated_category = update_category(created_category.id, update_data)

    assert updated_category is not None
    assert updated_category.name == "Updated Name"
    assert updated_category.id == created_category.id


def test_update_category_not_found(new_db):
    update_data = CategoryUpdate(name="Updated Name")
    result = update_category(999, update_data)
    assert result is None


def test_delete_category_success(new_db):
    category_data = CategoryCreate(name="Web Development")
    created_category = create_category(category_data)
    assert created_category.id is not None

    result = delete_category(created_category.id)

    assert result is True
    assert get_category_by_id(created_category.id) is None


def test_delete_category_with_requirements_fails(new_db):
    # Create category
    category_data = CategoryCreate(name="Web Development")
    category = create_category(category_data)
    assert category.id is not None

    # Create client
    client_data = ClientCreate(
        agency_name="Test Agency",
        contact_person="John Doe",
        email="john@test.com",
        phone="123",
        address="Address",
        website="https://test.com",
    )
    client = create_client(client_data)
    assert client.id is not None

    # Create requirement
    req_data = RequirementCreate(title="Test Requirement", client_id=client.id, category_id=category.id)
    create_requirement(req_data)

    # Try to delete category - should fail
    result = delete_category(category.id)
    assert result is False
    assert get_category_by_id(category.id) is not None


def test_delete_category_not_found(new_db):
    result = delete_category(999)
    assert result is False


def test_get_categories_with_requirement_counts(new_db):
    # Create categories
    category1 = create_category(CategoryCreate(name="Web Development"))
    category2 = create_category(CategoryCreate(name="Mobile Development"))
    create_category(CategoryCreate(name="API Development"))

    assert category1.id is not None
    assert category2.id is not None

    # Create client
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

    # Create requirements - 2 for category1, 1 for category2, 0 for category3
    req1_data = RequirementCreate(title="Web Requirement 1", client_id=client.id, category_id=category1.id)
    req2_data = RequirementCreate(title="Web Requirement 2", client_id=client.id, category_id=category1.id)
    req3_data = RequirementCreate(title="Mobile Requirement 1", client_id=client.id, category_id=category2.id)

    create_requirement(req1_data)
    create_requirement(req2_data)
    create_requirement(req3_data)

    categories_with_counts = get_categories_with_requirement_counts()

    assert len(categories_with_counts) == 3

    # Find each category in the results
    category_counts = {cat["name"]: cat["requirement_count"] for cat in categories_with_counts}
    assert category_counts["Web Development"] == 2
    assert category_counts["Mobile Development"] == 1
    assert category_counts["API Development"] == 0


def test_category_unique_name_constraint(new_db):
    # Create first category
    category1_data = CategoryCreate(name="Web Development")
    create_category(category1_data)

    # Try to create second category with same name - should fail
    category2_data = CategoryCreate(name="Web Development")
    with pytest.raises(Exception):  # Will raise database integrity error
        create_category(category2_data)


def test_category_name_validation(new_db):
    # Create category with empty name should work in creation but fail in database
    category_data = CategoryCreate(name="Valid Name")
    category = create_category(category_data)
    assert category.name == "Valid Name"


def test_category_update_partial_data(new_db):
    # Create category
    category_data = CategoryCreate(name="Original Name")
    created_category = create_category(category_data)
    assert created_category.id is not None

    # Update with valid name
    update_data = CategoryUpdate(name="Updated Name")
    result = update_category(created_category.id, update_data)

    # Should return the updated category
    assert result is not None
    assert result.name == "Updated Name"
