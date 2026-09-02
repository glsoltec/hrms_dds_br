import frappe
from frappe import _
from frappe.utils import getdate

from hrms_dds_br.permissions import PRIVILEGED_ROLES


MAX_ROWS = 5000


def execute(filters=None):
    filters = filters or {}
    validate_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def validate_filters(filters):
    if bool(filters.get("date_from")) != bool(filters.get("date_to")):
        frappe.throw(_("Informe as datas inicial e final juntas."))
    if filters.get("date_from") and getdate(filters["date_from"]) > getdate(filters["date_to"]):
        frappe.throw(_("A data inicial não pode ser posterior à data final."))

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


def get_report_filters(filters):
    return {
        key: value
        for key, value in {
            "date": ["between", [filters.get("date_from"), filters.get("date_to")]],
            "project": filters.get("project"),
            "topic": filters.get("topic"),
            "workflow_state": filters.get("workflow_state"),
        }.items()
        if value and (key != "date" or all(value[1]))
    }


def get_data(filters):
    employee = filters.get("employee")
    privileged = is_privileged()
    own_employees = None
    if not privileged:
        own_employees = get_user_employees()

    dds_list = frappe.get_all(
        "DDS",
        filters={"docstatus": ["<", 2], **get_report_filters(filters)},
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
        limit_page_length=MAX_ROWS + 1,
    )
    if len(dds_list) > MAX_ROWS:
        frappe.throw(
            _("O relatório excede o limite de {0} registros. Informe filtros mais específicos.").format(
                MAX_ROWS
            )
        )

    rows = []
    dds_names = [dds.name for dds in dds_list]
    participants_by_parent = get_participants(dds_names)
    for dds in dds_list:
        participants = participants_by_parent.get(dds.name, [])
        matches = select_matches(dds, participants, employee, privileged, own_employees)
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
                    "signed": _("Sim") if p.get("signed") else _("Não"),
                }
            )
            if len(rows) > MAX_ROWS:
                frappe.throw(
                    _("O relatório excede o limite de {0} linhas. Informe filtros mais específicos.").format(
                        MAX_ROWS
                    )
                )

    return rows


def get_participants(parents):
    if not parents:
        return {}

    participante = frappe.qb.DocType("DDS Participante")
    participants = (
        frappe.qb.from_(participante)
        .select(
            participante.parent,
            participante.employee,
            participante.present,
            participante.signature.isnotnull().as_("signed"),
        )
        .where(
            participante.parent.isin(parents)
            & (participante.parenttype == "DDS")
        )
        .orderby(participante.idx)
        .run(as_dict=True)
    )
    grouped = {}
    for participant in participants:
        grouped.setdefault(participant["parent"], []).append(participant)
    return grouped


def select_matches(dds, participants, employee, privileged, own_employees):
    if employee:
        matches = [p for p in participants if p["employee"] == employee]
        if dds.responsible == employee and not matches:
            matches = [{"employee": dds.responsible, "present": 0, "signed": 0}]
        return matches

    if privileged:
        return participants

    own = own_employees or set()
    matches = [p for p in participants if p["employee"] in own]
    if dds.responsible in own and not any(
        p["employee"] == dds.responsible for p in matches
    ):
        matches.append({"employee": dds.responsible, "present": 0, "signed": 0})
    return matches


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
