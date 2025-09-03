from nicegui import ui
from app.services.client_service import (
    get_clients_with_requirement_counts,
    get_client_by_id,
    create_client,
    update_client,
    delete_client,
)
from app.models import ClientCreate, ClientUpdate


def create():
    @ui.page("/clients")
    def clients_page():
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
                ui.label("Client Management").classes("text-xl font-bold")
                ui.button("← Back to Dashboard", on_click=lambda: ui.navigate.to("/dashboard")).props(
                    "flat text-color=white"
                )

        with ui.column().classes("w-full p-6 max-w-7xl mx-auto"):
            with ui.row().classes("justify-between items-center mb-6"):
                ui.label("Clients").classes("text-2xl font-bold text-gray-800")
                ui.button("Add New Client", on_click=lambda: show_client_form()).classes(
                    "bg-primary text-white px-4 py-2 rounded-lg hover:shadow-md"
                ).props("icon=add")

            @ui.refreshable
            def show_clients_table():
                clients = get_clients_with_requirement_counts()

                if not clients:
                    with ui.card().classes("p-8 text-center bg-gray-50"):
                        ui.icon("business", size="4rem").classes("text-gray-400 mb-4")
                        ui.label("No clients found").classes("text-xl text-gray-600 mb-2")
                        ui.label("Add your first client to get started").classes("text-gray-500")
                        ui.button("Add Client", on_click=lambda: show_client_form()).classes(
                            "bg-primary text-white px-4 py-2 rounded-lg mt-4"
                        ).props("icon=add")
                    return

                # Clients table
                columns = [
                    {"name": "agency_name", "label": "Agency Name", "field": "agency_name", "align": "left"},
                    {"name": "contact_person", "label": "Contact Person", "field": "contact_person", "align": "left"},
                    {"name": "email", "label": "Email", "field": "email", "align": "left"},
                    {"name": "phone", "label": "Phone", "field": "phone", "align": "left"},
                    {
                        "name": "requirement_count",
                        "label": "Requirements",
                        "field": "requirement_count",
                        "align": "center",
                    },
                    {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
                ]

                table = ui.table(columns=columns, rows=clients, row_key="id").classes("w-full")
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
                    client_id = e.args["id"]
                    if client_id is not None:
                        show_client_form(client_id)

                def handle_delete(e):
                    show_delete_confirmation(e.args["id"], e.args["agency_name"])

                def handle_view(e):
                    show_client_details(e.args["id"])

                table.on("edit", handle_edit)
                table.on("delete", handle_delete)
                table.on("view", handle_view)

            show_clients_table()

            def show_client_form(client_id: int | None = None):
                client = None
                if client_id:
                    client = get_client_by_id(client_id)
                    if client is None:
                        ui.notify("Client not found", type="negative")
                        return

                with ui.dialog() as dialog, ui.card().classes("w-96"):
                    ui.label("Edit Client" if client else "Add New Client").classes("text-lg font-bold mb-4")

                    agency_name = ui.input("Agency Name", value=client.agency_name if client else "").classes(
                        "w-full mb-2"
                    )
                    contact_person = ui.input("Contact Person", value=client.contact_person if client else "").classes(
                        "w-full mb-2"
                    )
                    email = ui.input("Email", value=client.email if client else "").classes("w-full mb-2")
                    phone = ui.input("Phone", value=client.phone if client else "").classes("w-full mb-2")
                    address = (
                        ui.textarea("Address", value=client.address if client else "")
                        .classes("w-full mb-2")
                        .props("rows=2")
                    )
                    website = ui.input("Website", value=client.website if client else "").classes("w-full mb-4")

                    with ui.row().classes("gap-2 justify-end w-full"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        ui.button("Save", on_click=lambda: save_client()).classes("bg-primary text-white")

                    def save_client():
                        if not agency_name.value or not contact_person.value or not email.value:
                            ui.notify("Please fill in required fields", type="negative")
                            return

                        try:
                            client_data = {
                                "agency_name": agency_name.value,
                                "contact_person": contact_person.value,
                                "email": email.value,
                                "phone": phone.value,
                                "address": address.value,
                                "website": website.value,
                            }

                            if client and client.id is not None:
                                result = update_client(client.id, ClientUpdate(**client_data))
                                if result:
                                    ui.notify("Client updated successfully", type="positive")
                                else:
                                    ui.notify("Failed to update client", type="negative")
                                    return
                            else:
                                result = create_client(ClientCreate(**client_data))
                                if result:
                                    ui.notify("Client created successfully", type="positive")
                                else:
                                    ui.notify("Failed to create client", type="negative")
                                    return

                            dialog.close()
                            show_clients_table.refresh()
                        except Exception as e:
                            ui.notify(f"Error: {str(e)}", type="negative")

                dialog.open()

            def show_delete_confirmation(client_id: int, agency_name: str):
                with ui.dialog() as dialog, ui.card():
                    ui.label("Confirm Deletion").classes("text-lg font-bold mb-4")
                    ui.label(f'Are you sure you want to delete "{agency_name}"?').classes("mb-2")
                    ui.label("This action cannot be undone. Clients with requirements cannot be deleted.").classes(
                        "text-sm text-gray-600 mb-4"
                    )

                    with ui.row().classes("gap-2 justify-end w-full"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        ui.button("Delete", on_click=lambda: delete_client_and_refresh()).classes(
                            "bg-negative text-white"
                        )

                    def delete_client_and_refresh():
                        if delete_client(client_id):
                            ui.notify("Client deleted successfully", type="positive")
                            dialog.close()
                            show_clients_table.refresh()
                        else:
                            ui.notify("Cannot delete client with requirements", type="negative")

                dialog.open()

            def show_client_details(client_id: int):
                client = get_client_by_id(client_id)
                if client is None:
                    ui.notify("Client not found", type="negative")
                    return

                with ui.dialog() as dialog, ui.card().classes("w-96"):
                    ui.label("Client Details").classes("text-lg font-bold mb-4")

                    with ui.column().classes("gap-2"):
                        ui.label(f"Agency: {client.agency_name}").classes("font-semibold")
                        ui.label(f"Contact: {client.contact_person}")
                        ui.label(f"Email: {client.email}")
                        ui.label(f"Phone: {client.phone}")
                        if client.address:
                            ui.label(f"Address: {client.address}")
                        if client.website:
                            ui.label(f"Website: {client.website}")
                        ui.label(f"Requirements: {len(client.requirements)}").classes("text-primary font-semibold")

                    with ui.row().classes("justify-end mt-4"):
                        ui.button("Close", on_click=lambda: dialog.close()).props("outline")

                dialog.open()
