from typing import List, Optional
from sqlmodel import select
from app.database import get_session
from app.models import Category, CategoryCreate, CategoryUpdate


def get_all_categories() -> List[Category]:
    """Get all categories ordered by name."""
    with get_session() as session:
        statement = select(Category).order_by(Category.name)
        return list(session.exec(statement))


def get_category_by_id(category_id: int) -> Optional[Category]:
    """Get a category by ID."""
    with get_session() as session:
        return session.get(Category, category_id)


def create_category(category_data: CategoryCreate) -> Category:
    """Create a new category."""
    with get_session() as session:
        category = Category(**category_data.model_dump())
        session.add(category)
        session.commit()
        session.refresh(category)
        return category


def update_category(category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
    """Update an existing category."""
    with get_session() as session:
        category = session.get(Category, category_id)
        if category is None:
            return None

        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        session.add(category)
        session.commit()
        session.refresh(category)
        return category


def delete_category(category_id: int) -> bool:
    """Delete a category if it has no associated requirements."""
    with get_session() as session:
        category = session.get(Category, category_id)
        if category is None:
            return False

        # Check if category has requirements
        if category.requirements:
            return False

        session.delete(category)
        session.commit()
        return True


def get_categories_with_requirement_counts() -> List[dict]:
    """Get all categories with their requirement counts."""
    with get_session() as session:
        categories = session.exec(select(Category).order_by(Category.name)).all()
        return [
            {
                "id": category.id,
                "name": category.name,
                "requirement_count": len(category.requirements) if category.requirements else 0,
            }
            for category in categories
        ]
