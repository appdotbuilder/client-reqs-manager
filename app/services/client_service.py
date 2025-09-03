from typing import List, Optional
from sqlmodel import select
from app.database import get_session
from app.models import Client, ClientCreate, ClientUpdate


def get_all_clients() -> List[Client]:
    """Get all clients ordered by agency name."""
    with get_session() as session:
        statement = select(Client).order_by(Client.agency_name)
        return list(session.exec(statement))


def get_client_by_id(client_id: int) -> Optional[Client]:
    """Get a client by ID."""
    with get_session() as session:
        return session.get(Client, client_id)


def create_client(client_data: ClientCreate) -> Client:
    """Create a new client."""
    with get_session() as session:
        client = Client(**client_data.model_dump())
        session.add(client)
        session.commit()
        session.refresh(client)
        return client


def update_client(client_id: int, client_data: ClientUpdate) -> Optional[Client]:
    """Update an existing client."""
    with get_session() as session:
        client = session.get(Client, client_id)
        if client is None:
            return None

        update_data = client_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)

        session.add(client)
        session.commit()
        session.refresh(client)
        return client


def delete_client(client_id: int) -> bool:
    """Delete a client if it has no associated requirements."""
    with get_session() as session:
        client = session.get(Client, client_id)
        if client is None:
            return False

        # Check if client has requirements
        if client.requirements:
            return False

        session.delete(client)
        session.commit()
        return True


def get_clients_with_requirement_counts() -> List[dict]:
    """Get all clients with their requirement counts."""
    with get_session() as session:
        clients = session.exec(select(Client).order_by(Client.agency_name)).all()
        return [
            {
                "id": client.id,
                "agency_name": client.agency_name,
                "contact_person": client.contact_person,
                "email": client.email,
                "phone": client.phone,
                "website": client.website,
                "requirement_count": len(client.requirements) if client.requirements else 0,
            }
            for client in clients
        ]
