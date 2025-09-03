from app.database import create_tables
from nicegui import ui
from app.ui import dashboard, client_management, requirement_management, settings


def startup() -> None:
    # this function is called before the first request
    create_tables()

    # Register UI modules
    dashboard.create()
    client_management.create()
    requirement_management.create()
    settings.create()

    @ui.page("/")
    def index():
        ui.navigate.to("/dashboard")
