import frappe
from frappe import _

from hrms_dds_br.permissions import PRIVILEGED_ROLES


def execute(filters=None):
    filters = filters or {}
    validate_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def validate_filters(filters):
    user = frappe.session.user
    roles = set(frappe.get_roles(user))
    if roles & PRIVILEGED_ROLES:
        return

    employee = filters.get("employee")
    if not employee:
        return

    employees = {
        row.name
        for row in frappe.get_all(
            "Employee",
            filters={"user_id": user, "status": "Active"},
            fields=["name"],
        )
    }
    if employee not in employees:
        frappe.throw(
            _("Você não tem permissão para consultar o histórico deste empregado."),
            frappe.PermissionError,
        )


def get_columns():
    return [
        {
            "label": _("DDS"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "DDS",
            "width": 140,
        },
        {"label": _("Data"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": _("Hora"), "fieldname": "time", "fieldtype": "Time", "width": 90},
        {
            "label": _("Projeto/Obra"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 180,
        },
        {
            "label": _("Cliente"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 160,
        },
        {"label": _("Tema"), "fieldname": "topic", "fieldtype": "Data", "width": 180},
        {
            "label": _("Responsável"),
            "fieldname": "responsible",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 150,
        },
        {
            "label": _("Situação"),
            "fieldname": "workflow_state",
            "fieldtype": "Data",
            "width": 150,
        },
        {"label": _("Empregado"), "fieldname": "employee", "fieldtype": "Data", "width": 140},
        {"label": _("Presente"), "fieldname": "present", "fieldtype": "Data", "width": 90},
        {"label": _("Assinou"), "fieldname": "signed", "fieldtype": "Data", "width": 90},
    ]


def get_data(filters):
    employee = filters.get("employee")
    privileged = is_privileged()
    own_employees = None
    if not privileged:
        own_employees = get_user_employees()

    dds_list = frappe.get_all(
        "DDS",
        filters={"docstatus": ["<", 2]},
        fields=[
            "name",
            "date",
            "time",
            "project",
            "customer",
            "topic",
            "responsible",
            "workflow_state",
        ],
        order_by="date desc, name desc",
    )

    rows = []
    for dds in dds_list:
        participants = frappe.get_all(
            "DDS Participante",
            filters={"parent": dds.name, "parenttype": "DDS"},
            fields=["employee", "present", "signature"],
            order_by="idx asc",
        )

        if employee:
            matches = [p for p in participants if p.employee == employee]
            if dds.responsible == employee and not matches:
                matches = [
                    {"employee": dds.responsible, "present": 0, "signature": None}
                ]
        elif privileged:
            matches = participants
        else:
            matches = [p for p in participants if p.employee in own_employees]

        for p in matches:
            rows.append(
                {
                    "name": dds.name,
                    "date": dds.date,
                    "time": dds.time,
                    "project": dds.project,
                    "customer": dds.customer,
                    "topic": dds.topic,
                    "responsible": dds.responsible,
                    "workflow_state": dds.workflow_state,
                    "employee": p["employee"],
                    "present": _("Sim") if p.get("present") else _("Não"),
                    "signed": _("Sim") if p.get("signature") else _("Não"),
                }
            )

    return rows


def is_privileged():
    roles = set(frappe.get_roles())
    return bool(roles & PRIVILEGED_ROLES)


def get_user_employees():
    return set(
        frappe.get_all(
            "Employee",
            filters={"user_id": frappe.session.user, "status": "Active"},
            pluck="name",
        )
    )