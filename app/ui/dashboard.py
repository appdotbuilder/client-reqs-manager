from nicegui import ui
from app.services.requirement_service import get_requirements_summary
from app.services.client_service import get_all_clients
from app.services.category_service import get_all_categories


def create():
    @ui.page("/dashboard")
    def dashboard():
        ui.colors(
            primary="#2563eb",
            secondary="#64748b",
            accent="#10b981",
            positive="#10b981",
            negative="#ef4444",
            warning="#f59e0b",
            info="#3b82f6",
        )

        with ui.header().classes("bg-primary text-white shadow-lg"):
            ui.label("Requirements Management").classes("text-xl font-bold")

        with ui.row().classes("w-full p-6"):
            # Sidebar navigation
            with ui.column().classes("w-64 bg-white rounded-lg shadow-md p-4"):
                ui.label("Navigation").classes("text-lg font-bold mb-4 text-gray-800")

                navigation_items = [
                    ("Dashboard", "/dashboard", "dashboard"),
                    ("Requirements", "/requirements", "assignment"),
                    ("Clients", "/clients", "business"),
                    ("Settings", "/settings", "settings"),
                ]

                for label, route, icon in navigation_items:
                    ui.button(label, on_click=lambda _, r=route: ui.navigate.to(r)).props(
                        f"flat icon={icon} align=left"
                    ).classes("w-full justify-start mb-2 text-gray-700 hover:bg-gray-100")

            # Main content area
            with ui.column().classes("flex-1 ml-6"):
                ui.label("Dashboard Overview").classes("text-3xl font-bold text-gray-800 mb-6")

                @ui.refreshable
                def show_summary():
                    summary = get_requirements_summary()
                    clients_count = len(get_all_clients())
                    categories_count = len(get_all_categories())

                    # Summary cards
                    with ui.row().classes("gap-6 mb-8 w-full"):
                        # Total requirements
                        with ui.card().classes(
                            "p-6 bg-white shadow-lg rounded-xl hover:shadow-xl transition-shadow min-w-48"
                        ):
                            ui.label("Total Requirements").classes("text-sm text-gray-500 uppercase tracking-wider")
                            ui.label(str(summary["total"])).classes("text-3xl font-bold text-primary mt-2")

                        # Clients
                        with ui.card().classes(
                            "p-6 bg-white shadow-lg rounded-xl hover:shadow-xl transition-shadow min-w-48"
                        ):
                            ui.label("Active Clients").classes("text-sm text-gray-500 uppercase tracking-wider")
                            ui.label(str(clients_count)).classes("text-3xl font-bold text-info mt-2")

                        # Categories
                        with ui.card().classes(
                            "p-6 bg-white shadow-lg rounded-xl hover:shadow-xl transition-shadow min-w-48"
                        ):
                            ui.label("Categories").classes("text-sm text-gray-500 uppercase tracking-wider")
                            ui.label(str(categories_count)).classes("text-3xl font-bold text-accent mt-2")

                        # Overdue
                        with ui.card().classes(
                            "p-6 bg-white shadow-lg rounded-xl hover:shadow-xl transition-shadow min-w-48"
                        ):
                            ui.label("Overdue Items").classes("text-sm text-gray-500 uppercase tracking-wider")
                            ui.label(str(summary["overdue"])).classes("text-3xl font-bold text-negative mt-2")

                    # Status and Priority breakdown
                    with ui.row().classes("gap-6 w-full"):
                        # Status breakdown
                        with ui.card().classes("p-6 bg-white shadow-lg rounded-xl flex-1"):
                            ui.label("Requirements by Status").classes("text-lg font-bold text-gray-800 mb-4")
                            for status, count in summary["by_status"].items():
                                with ui.row().classes("justify-between items-center mb-2"):
                                    ui.label(status).classes("text-gray-700")
                                    ui.label(str(count)).classes("font-bold text-primary")

                        # Priority breakdown
                        with ui.card().classes("p-6 bg-white shadow-lg rounded-xl flex-1"):
                            ui.label("Requirements by Priority").classes("text-lg font-bold text-gray-800 mb-4")
                            priority_colors = {"High": "text-negative", "Medium": "text-warning", "Low": "text-accent"}
                            for priority, count in summary["by_priority"].items():
                                with ui.row().classes("justify-between items-center mb-2"):
                                    ui.label(priority).classes("text-gray-700")
                                    ui.label(str(count)).classes(
                                        f"font-bold {priority_colors.get(priority, 'text-primary')}"
                                    )

                show_summary()

                # Quick actions
                with ui.card().classes("p-6 bg-white shadow-lg rounded-xl mt-6"):
                    ui.label("Quick Actions").classes("text-lg font-bold text-gray-800 mb-4")
                    with ui.row().classes("gap-4"):
                        ui.button("New Requirement", on_click=lambda: ui.navigate.to("/requirements")).classes(
                            "bg-primary text-white px-6 py-2 rounded-lg hover:shadow-md"
                        ).props("icon=add")
                        ui.button("Manage Clients", on_click=lambda: ui.navigate.to("/clients")).classes(
                            "bg-info text-white px-6 py-2 rounded-lg hover:shadow-md"
                        ).props("icon=business")
                        ui.button("Settings", on_click=lambda _: ui.navigate.to("/settings")).classes(
                            "bg-secondary text-white px-6 py-2 rounded-lg hover:shadow-md"
                        ).props("icon=settings")

                # Refresh button
                with ui.row().classes("mt-6"):
                    ui.button("Refresh Data", on_click=show_summary.refresh).classes(
                        "bg-accent text-white px-4 py-2 rounded-lg hover:shadow-md"
                    ).props("icon=refresh")
