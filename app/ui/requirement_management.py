from datetime import date
from nicegui import ui
from app.services.requirement_service import (
    get_all_requirements,
    get_requirement_by_id,
    create_requirement,
    update_requirement,
    delete_requirement,
)
from app.services.client_service import get_all_clients
from app.services.category_service import get_all_categories
from app.services.team_member_service import get_all_team_members
from app.models import RequirementCreate, RequirementUpdate, Priority, Status


def create():
    @ui.page("/requirements")
    def requirements_page():
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
            with ui.row().classes("w-full justify-between items-center"):
                ui.label("Requirements Management").classes("text-xl font-bold")
                ui.button("← Back to Dashboard", on_click=lambda: ui.navigate.to("/dashboard")).props(
                    "flat text-color=white"
                )

        with ui.column().classes("w-full p-6 max-w-7xl mx-auto"):
            with ui.row().classes("justify-between items-center mb-6"):
                ui.label("Requirements").classes("text-2xl font-bold text-gray-800")
                ui.button("Add New Requirement", on_click=lambda: show_requirement_form()).classes(
                    "bg-primary text-white px-4 py-2 rounded-lg hover:shadow-md"
                ).props("icon=add")

            @ui.refreshable
            def show_requirements_table():
                requirements = get_all_requirements()

                if not requirements:
                    with ui.card().classes("p-8 text-center bg-gray-50"):
                        ui.icon("assignment", size="4rem").classes("text-gray-400 mb-4")
                        ui.label("No requirements found").classes("text-xl text-gray-600 mb-2")
                        ui.label("Add your first requirement to get started").classes("text-gray-500")
                        ui.button("Add Requirement", on_click=lambda: show_requirement_form()).classes(
                            "bg-primary text-white px-4 py-2 rounded-lg mt-4"
                        ).props("icon=add")
                    return

                # Format data for table
                table_data = []
                for req in requirements:
                    table_data.append(
                        {
                            "id": req.id,
                            "title": req.title,
                            "client": req.client.agency_name if req.client else "Unknown",
                            "category": req.category.name if req.category else "Unknown",
                            "priority": req.priority.value,
                            "status": req.status.value,
                            "assigned_to": req.team_member.name if req.team_member else "Unassigned",
                            "due_date": req.due_date.isoformat() if req.due_date else "",
                            "created_at": req.created_at.strftime("%Y-%m-%d"),
                        }
                    )

                # Requirements table
                columns = [
                    {"name": "title", "label": "Title", "field": "title", "align": "left"},
                    {"name": "client", "label": "Client", "field": "client", "align": "left"},
                    {"name": "category", "label": "Category", "field": "category", "align": "left"},
                    {"name": "priority", "label": "Priority", "field": "priority", "align": "center"},
                    {"name": "status", "label": "Status", "field": "status", "align": "center"},
                    {"name": "assigned_to", "label": "Assigned To", "field": "assigned_to", "align": "left"},
                    {"name": "due_date", "label": "Due Date", "field": "due_date", "align": "center"},
                    {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
                ]

                table = ui.table(columns=columns, rows=table_data, row_key="id").classes("w-full")

                # Custom slots for priority and status with colors
                table.add_slot(
                    "body-cell-priority",
                    """
                    <q-td :props="props">
                        <q-badge :color="props.value === 'High' ? 'negative' : props.value === 'Medium' ? 'warning' : 'positive'" 
                                 :label="props.value" />
                    </q-td>
                """,
                )

                table.add_slot(
                    "body-cell-status",
                    """
                    <q-td :props="props">
                        <q-badge :color="props.value === 'Done' ? 'positive' : props.value === 'In Progress' ? 'info' : 'secondary'" 
                                 :label="props.value" />
                    </q-td>
                """,
                )

                table.add_slot(
                    "body-cell-actions",
                    """
                    <q-td :props="props">
                        <q-btn flat dense icon="edit" color="primary" size="sm" @click="$parent.$emit('edit', props.row)" />
                        <q-btn flat dense icon="delete" color="negative" size="sm" @click="$parent.$emit('delete', props.row)" />
                        <q-btn flat dense icon="visibility" color="info" size="sm" @click="$parent.$emit('view', props.row)" />
                    </q-td>
                """,
                )

                def handle_edit(e):
                    requirement_id = e.args["id"]
                    if requirement_id is not None:
                        show_requirement_form(requirement_id)

                def handle_delete(e):
                    show_delete_confirmation(e.args["id"], e.args["title"])

                def handle_view(e):
                    show_requirement_details(e.args["id"])

                table.on("edit", handle_edit)
                table.on("delete", handle_delete)
                table.on("view", handle_view)

            show_requirements_table()

            def show_requirement_form(requirement_id: int | None = None):
                requirement = None
                if requirement_id:
                    requirement = get_requirement_by_id(requirement_id)
                    if requirement is None:
                        ui.notify("Requirement not found", type="negative")
                        return

                # Get options for dropdowns
                clients = get_all_clients()
                categories = get_all_categories()
                team_members = get_all_team_members()

                if not clients:
                    ui.notify("Please add clients first", type="negative")
                    return
                if not categories:
                    ui.notify("Please add categories first", type="negative")
                    return

                with ui.dialog() as dialog, ui.card().classes("w-[600px]"):
                    ui.label("Edit Requirement" if requirement else "Add New Requirement").classes(
                        "text-lg font-bold mb-4"
                    )

                    title_input = ui.input("Title", value=requirement.title if requirement else "").classes(
                        "w-full mb-2"
                    )

                    description_input = (
                        ui.textarea("Description", value=requirement.description if requirement else "")
                        .classes("w-full mb-2")
                        .props("rows=3")
                    )

                    # Client dropdown
                    client_options = {c.id: c.agency_name for c in clients}
                    client_select = ui.select(
                        label="Client", options=client_options, value=requirement.client_id if requirement else None
                    ).classes("w-full mb-2")

                    # Category dropdown
                    category_options = {c.id: c.name for c in categories}
                    category_select = ui.select(
                        label="Category",
                        options=category_options,
                        value=requirement.category_id if requirement else None,
                    ).classes("w-full mb-2")

                    # Priority dropdown
                    priority_options = {p.value: p.value for p in Priority}
                    priority_select = ui.select(
                        label="Priority",
                        options=priority_options,
                        value=requirement.priority.value if requirement else Priority.MEDIUM.value,
                    ).classes("w-full mb-2")

                    # Status dropdown
                    status_options = {s.value: s.value for s in Status}
                    status_select = ui.select(
                        label="Status",
                        options=status_options,
                        value=requirement.status.value if requirement else Status.TODO.value,
                    ).classes("w-full mb-2")

                    # Team member dropdown (optional)
                    team_member_options = {tm.id: tm.name for tm in team_members}
                    team_member_options[None] = "Unassigned"
                    team_member_select = ui.select(
                        label="Assigned To",
                        options=team_member_options,
                        value=requirement.team_member_id if requirement else None,
                    ).classes("w-full mb-2")

                    # Due date
                    due_date_input = (
                        ui.date(
                            value=requirement.due_date.isoformat() if requirement and requirement.due_date else None
                        )
                        .classes("w-full mb-4")
                        .props('label="Due Date"')
                    )

                    with ui.row().classes("gap-2 justify-end w-full"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        ui.button("Save", on_click=lambda: save_requirement()).classes("bg-primary text-white")

                    def save_requirement():
                        if not title_input.value or not client_select.value or not category_select.value:
                            ui.notify("Please fill in required fields", type="negative")
                            return

                        try:
                            requirement_data = {
                                "title": title_input.value,
                                "description": description_input.value or "",
                                "client_id": client_select.value,
                                "category_id": category_select.value,
                                "priority": Priority(priority_select.value),
                                "status": Status(status_select.value),
                                "team_member_id": team_member_select.value
                                if team_member_select.value != "None"
                                else None,
                                "due_date": due_date_input.value,
                            }

                            if requirement and requirement.id is not None:
                                result = update_requirement(requirement.id, RequirementUpdate(**requirement_data))
                                if result:
                                    ui.notify("Requirement updated successfully", type="positive")
                                else:
                                    ui.notify("Failed to update requirement", type="negative")
                                    return
                            else:
                                result = create_requirement(RequirementCreate(**requirement_data))
                                if result:
                                    ui.notify("Requirement created successfully", type="positive")
                                else:
                                    ui.notify("Failed to create requirement", type="negative")
                                    return

                            dialog.close()
                            show_requirements_table.refresh()
                        except Exception as e:
                            ui.notify(f"Error: {str(e)}", type="negative")

                dialog.open()

            def show_delete_confirmation(requirement_id: int, title: str):
                with ui.dialog() as dialog, ui.card():
                    ui.label("Confirm Deletion").classes("text-lg font-bold mb-4")
                    ui.label(f'Are you sure you want to delete "{title}"?').classes("mb-2")
                    ui.label("This action cannot be undone.").classes("text-sm text-gray-600 mb-4")

                    with ui.row().classes("gap-2 justify-end w-full"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        ui.button("Delete", on_click=lambda: delete_requirement_and_refresh()).classes(
                            "bg-negative text-white"
                        )

                    def delete_requirement_and_refresh():
                        if delete_requirement(requirement_id):
                            ui.notify("Requirement deleted successfully", type="positive")
                            dialog.close()
                            show_requirements_table.refresh()
                        else:
                            ui.notify("Failed to delete requirement", type="negative")

                dialog.open()

            def show_requirement_details(requirement_id: int):
                requirement = get_requirement_by_id(requirement_id)
                if requirement is None:
                    ui.notify("Requirement not found", type="negative")
                    return

                with ui.dialog() as dialog, ui.card().classes("w-[500px]"):
                    ui.label("Requirement Details").classes("text-lg font-bold mb-4")

                    with ui.column().classes("gap-3"):
                        ui.label(f"Title: {requirement.title}").classes("font-semibold text-lg")
                        if requirement.description:
                            ui.label("Description:").classes("font-semibold")
                            ui.label(requirement.description).classes("text-gray-700 whitespace-pre-wrap")

                        ui.label(f"Client: {requirement.client.agency_name}").classes("text-primary")
                        ui.label(f"Category: {requirement.category.name}").classes("text-info")

                        with ui.row().classes("gap-4"):
                            priority_color = {"High": "negative", "Medium": "warning", "Low": "positive"}[
                                requirement.priority.value
                            ]
                            ui.badge(requirement.priority.value, color=priority_color)

                            status_color = {"Done": "positive", "In Progress": "info", "To Do": "secondary"}[
                                requirement.status.value
                            ]
                            ui.badge(requirement.status.value, color=status_color)

                        if requirement.team_member:
                            ui.label(f"Assigned to: {requirement.team_member.name}").classes("text-accent")
                        else:
                            ui.label("Assigned to: Unassigned").classes("text-gray-500")

                        if requirement.due_date:
                            today = date.today()
                            is_overdue = requirement.due_date < today and requirement.status != Status.DONE
                            due_color = "text-negative" if is_overdue else "text-gray-700"
                            ui.label(f"Due Date: {requirement.due_date.strftime('%Y-%m-%d')}").classes(due_color)

                        ui.label(f"Created: {requirement.created_at.strftime('%Y-%m-%d %H:%M')}").classes(
                            "text-sm text-gray-500"
                        )
                        if requirement.updated_at != requirement.created_at:
                            ui.label(f"Updated: {requirement.updated_at.strftime('%Y-%m-%d %H:%M')}").classes(
                                "text-sm text-gray-500"
                            )

                    with ui.row().classes("justify-end mt-4"):
                        ui.button("Close", on_click=lambda: dialog.close()).props("outline")

                dialog.open()
