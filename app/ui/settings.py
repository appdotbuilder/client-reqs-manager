from nicegui import ui
from app.services.category_service import (
    get_categories_with_requirement_counts,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
)
from app.services.team_member_service import (
    get_team_members_with_requirement_counts,
    get_team_member_by_id,
    create_team_member,
    update_team_member,
    delete_team_member,
)
from app.models import CategoryCreate, CategoryUpdate, TeamMemberCreate, TeamMemberUpdate


def create():
    @ui.page("/settings")
    def settings_page():
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
                ui.label("Settings").classes("text-xl font-bold")
                ui.button("← Back to Dashboard", on_click=lambda: ui.navigate.to("/dashboard")).props(
                    "flat text-color=white"
                )

        with ui.column().classes("w-full p-6 max-w-6xl mx-auto"):
            ui.label("Application Settings").classes("text-2xl font-bold text-gray-800 mb-6")

            # Categories Section
            with ui.card().classes("p-6 mb-6 shadow-lg rounded-xl"):
                with ui.row().classes("justify-between items-center mb-4"):
                    ui.label("Categories").classes("text-xl font-bold text-gray-800")
                    ui.button("Add Category", on_click=lambda: show_category_form()).classes(
                        "bg-primary text-white px-4 py-2 rounded-lg hover:shadow-md"
                    ).props("icon=add")

                @ui.refreshable
                def show_categories_section():
                    categories = get_categories_with_requirement_counts()

                    if not categories:
                        with ui.row().classes("items-center justify-center p-8 bg-gray-50 rounded-lg"):
                            ui.icon("category", size="2rem").classes("text-gray-400 mr-4")
                            ui.label("No categories found. Add your first category to organize requirements.").classes(
                                "text-gray-600"
                            )
                        return

                    # Categories table
                    columns = [
                        {"name": "name", "label": "Category Name", "field": "name", "align": "left"},
                        {
                            "name": "requirement_count",
                            "label": "Requirements Count",
                            "field": "requirement_count",
                            "align": "center",
                        },
                        {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
                    ]

                    table = ui.table(columns=columns, rows=categories, row_key="id").classes("w-full")
                    table.add_slot(
                        "body-cell-actions",
                        """
                        <q-td :props="props">
                            <q-btn flat dense icon="edit" color="primary" size="sm" @click="$parent.$emit('edit', props.row)" />
                            <q-btn flat dense icon="delete" color="negative" size="sm" @click="$parent.$emit('delete', props.row)" />
                        </q-td>
                    """,
                    )

                    def handle_edit_category(e):
                        category_id = e.args["id"]
                        if category_id is not None:
                            show_category_form(category_id)

                    def handle_delete_category(e):
                        show_category_delete_confirmation(e.args["id"], e.args["name"])

                    table.on("edit", handle_edit_category)
                    table.on("delete", handle_delete_category)

                show_categories_section()

            # Team Members Section
            with ui.card().classes("p-6 shadow-lg rounded-xl"):
                with ui.row().classes("justify-between items-center mb-4"):
                    ui.label("Team Members").classes("text-xl font-bold text-gray-800")
                    ui.button("Add Team Member", on_click=lambda: show_team_member_form()).classes(
                        "bg-info text-white px-4 py-2 rounded-lg hover:shadow-md"
                    ).props("icon=person_add")

                @ui.refreshable
                def show_team_members_section():
                    team_members = get_team_members_with_requirement_counts()

                    if not team_members:
                        with ui.row().classes("items-center justify-center p-8 bg-gray-50 rounded-lg"):
                            ui.icon("group", size="2rem").classes("text-gray-400 mr-4")
                            ui.label("No team members found. Add team members to assign requirements.").classes(
                                "text-gray-600"
                            )
                        return

                    # Team members table
                    columns = [
                        {"name": "name", "label": "Team Member Name", "field": "name", "align": "left"},
                        {
                            "name": "requirement_count",
                            "label": "Assigned Requirements",
                            "field": "requirement_count",
                            "align": "center",
                        },
                        {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
                    ]

                    table = ui.table(columns=columns, rows=team_members, row_key="id").classes("w-full")
                    table.add_slot(
                        "body-cell-actions",
                        """
                        <q-td :props="props">
                            <q-btn flat dense icon="edit" color="primary" size="sm" @click="$parent.$emit('edit', props.row)" />
                            <q-btn flat dense icon="delete" color="negative" size="sm" @click="$parent.$emit('delete', props.row)" />
                        </q-td>
                    """,
                    )

                    def handle_edit_team_member(e):
                        team_member_id = e.args["id"]
                        if team_member_id is not None:
                            show_team_member_form(team_member_id)

                    def handle_delete_team_member(e):
                        show_team_member_delete_confirmation(e.args["id"], e.args["name"])

                    table.on("edit", handle_edit_team_member)
                    table.on("delete", handle_delete_team_member)

                show_team_members_section()

            # Category form functions
            def show_category_form(category_id: int | None = None):
                category = None
                if category_id:
                    category = get_category_by_id(category_id)
                    if category is None:
                        ui.notify("Category not found", type="negative")
                        return

                with ui.dialog() as dialog, ui.card().classes("w-80"):
                    ui.label("Edit Category" if category else "Add New Category").classes("text-lg font-bold mb-4")

                    name_input = ui.input("Category Name", value=category.name if category else "").classes(
                        "w-full mb-4"
                    )

                    with ui.row().classes("gap-2 justify-end w-full"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        ui.button("Save", on_click=lambda: save_category()).classes("bg-primary text-white")

                    def save_category():
                        if not name_input.value.strip():
                            ui.notify("Please enter a category name", type="negative")
                            return

                        try:
                            if category and category.id is not None:
                                result = update_category(category.id, CategoryUpdate(name=name_input.value.strip()))
                                if result:
                                    ui.notify("Category updated successfully", type="positive")
                                else:
                                    ui.notify("Failed to update category", type="negative")
                                    return
                            else:
                                result = create_category(CategoryCreate(name=name_input.value.strip()))
                                if result:
                                    ui.notify("Category created successfully", type="positive")
                                else:
                                    ui.notify("Failed to create category", type="negative")
                                    return

                            dialog.close()
                            show_categories_section.refresh()
                        except Exception as e:
                            ui.notify(f"Error: {str(e)}", type="negative")

                dialog.open()

            def show_category_delete_confirmation(category_id: int, name: str):
                with ui.dialog() as dialog, ui.card():
                    ui.label("Confirm Deletion").classes("text-lg font-bold mb-4")
                    ui.label(f'Are you sure you want to delete the category "{name}"?').classes("mb-2")
                    ui.label("Categories with requirements cannot be deleted.").classes("text-sm text-gray-600 mb-4")

                    with ui.row().classes("gap-2 justify-end w-full"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        ui.button("Delete", on_click=lambda: delete_category_and_refresh()).classes(
                            "bg-negative text-white"
                        )

                    def delete_category_and_refresh():
                        if delete_category(category_id):
                            ui.notify("Category deleted successfully", type="positive")
                            dialog.close()
                            show_categories_section.refresh()
                        else:
                            ui.notify("Cannot delete category with requirements", type="negative")

                dialog.open()

            # Team member form functions
            def show_team_member_form(team_member_id: int | None = None):
                team_member = None
                if team_member_id:
                    team_member = get_team_member_by_id(team_member_id)
                    if team_member is None:
                        ui.notify("Team member not found", type="negative")
                        return

                with ui.dialog() as dialog, ui.card().classes("w-80"):
                    ui.label("Edit Team Member" if team_member else "Add New Team Member").classes(
                        "text-lg font-bold mb-4"
                    )

                    name_input = ui.input("Team Member Name", value=team_member.name if team_member else "").classes(
                        "w-full mb-4"
                    )

                    with ui.row().classes("gap-2 justify-end w-full"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        ui.button("Save", on_click=lambda: save_team_member()).classes("bg-info text-white")

                    def save_team_member():
                        if not name_input.value.strip():
                            ui.notify("Please enter a team member name", type="negative")
                            return

                        try:
                            if team_member and team_member.id is not None:
                                result = update_team_member(
                                    team_member.id, TeamMemberUpdate(name=name_input.value.strip())
                                )
                                if result:
                                    ui.notify("Team member updated successfully", type="positive")
                                else:
                                    ui.notify("Failed to update team member", type="negative")
                                    return
                            else:
                                result = create_team_member(TeamMemberCreate(name=name_input.value.strip()))
                                if result:
                                    ui.notify("Team member created successfully", type="positive")
                                else:
                                    ui.notify("Failed to create team member", type="negative")
                                    return

                            dialog.close()
                            show_team_members_section.refresh()
                        except Exception as e:
                            ui.notify(f"Error: {str(e)}", type="negative")

                dialog.open()

            def show_team_member_delete_confirmation(team_member_id: int, name: str):
                with ui.dialog() as dialog, ui.card():
                    ui.label("Confirm Deletion").classes("text-lg font-bold mb-4")
                    ui.label(f'Are you sure you want to delete the team member "{name}"?').classes("mb-2")
                    ui.label("Team members with assigned requirements cannot be deleted.").classes(
                        "text-sm text-gray-600 mb-4"
                    )

                    with ui.row().classes("gap-2 justify-end w-full"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        ui.button("Delete", on_click=lambda: delete_team_member_and_refresh()).classes(
                            "bg-negative text-white"
                        )

                    def delete_team_member_and_refresh():
                        if delete_team_member(team_member_id):
                            ui.notify("Team member deleted successfully", type="positive")
                            dialog.close()
                            show_team_members_section.refresh()
                        else:
                            ui.notify("Cannot delete team member with assigned requirements", type="negative")

                dialog.open()
