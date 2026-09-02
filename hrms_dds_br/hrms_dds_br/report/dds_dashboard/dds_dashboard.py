import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Max
from frappe.utils import add_days, getdate

from hrms_dds_br.permissions import PRIVILEGED_ROLES


def execute(filters=None):
    filters = filters or {}
    if not (set(frappe.get_roles()) & PRIVILEGED_ROLES):
        frappe.throw(
            _("Você não tem permissão para consultar o painel de DDS."),
            frappe.PermissionError,
        )

    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(filters)
    chart = get_chart(filters)
    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "label": _("Projeto/Obra"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 200,
        },
        {
            "label": _("Cliente"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 160,
        },
        {"label": _("Situação"), "fieldname": "status", "fieldtype": "Data", "width": 110},
        {"label": _("DDS registrados"), "fieldname": "total_dds", "fieldtype": "Int", "width": 120},
        {
            "label": _("Último DDS"),
            "fieldname": "last_dds_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Dias desde o último DDS"),
            "fieldname": "days_since_last",
            "fieldtype": "Int",
            "width": 150,
        },
        {
            "label": _("Alerta"),
            "fieldname": "alert",
            "fieldtype": "Data",
            "width": 90,
        },
    ]


def get_data(filters):
    threshold = get_alert_days()
    Project = DocType("Project")
    DDS = DocType("DDS")
    rows = (
        frappe.qb.from_(Project)
        .left_join(DDS)
        .on(DDS.project == Project.name)
        .select(
            Project.name.as_("project"),
            Project.customer,
            Project.status,
            Count(DDS.name).as_("total_dds"),
            Max(DDS.date).as_("last_dds_date"),
        )
        .where(Project.status.notin(["Closed", "Completed"]))
        .groupby(Project.name)
        .orderby(Project.name)
        .run(as_dict=True)
    )

    today = getdate()
    data = []
    for row in rows:
        last = getdate(row.get("last_dds_date")) if row.get("last_dds_date") else None
        days = (today - last).days if last else None
        if last is None or days > threshold:
            alert = _("Sim")
        else:
            alert = _("Não")
        data.append(
            {
                "project": row.project,
                "customer": row.customer,
                "status": row.status,
                "total_dds": row.total_dds,
                "last_dds_date": row.last_dds_date,
                "days_since_last": days if days is not None else _("Sem DDS"),
                "alert": alert,
            }
        )
    return data


def get_summary(filters):
    date_from, date_to = _get_date_range(filters)
    base = {"date": ["between", [date_from, date_to]], "docstatus": ["<", 2]}
    submitted = frappe.db.count(
        "DDS",
        filters={**base, "workflow_state": "Realizado/Enviado"},
    )
    cancelled = frappe.db.count("DDS", filters={"workflow_state": "Cancelado"})
    total = frappe.db.count("DDS", filters=base)
    alert_count = len([row for row in get_data({}) if row["alert"] == _("Sim")])
    return [
        {"value": total, "label": _("DDS no período"), "indicator": "blue"},
        {"value": submitted, "label": _("Realizados/Enviados"), "indicator": "green"},
        {"value": cancelled, "label": _("Cancelados"), "indicator": "red"},
        {"value": alert_count, "label": _("Projetos em alerta"), "indicator": "orange"},
    ]


def get_chart(filters):
    date_from, date_to = _get_date_range(filters)
    dds_list = frappe.get_all(
        "DDS",
        filters={"date": ["between", [date_from, date_to]], "docstatus": ["<", 2]},
        fields=["date"],
        order_by="date",
    )
    buckets = {}
    for row in dds_list:
        if not row.date:
            continue
        key = getdate(row.date).strftime("%Y-%m")
        buckets[key] = buckets.get(key, 0) + 1

    labels = sorted(buckets)
    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("DDS"), "values": [buckets[k] for k in labels]}],
        },
        "type": "bar",
    }


def _get_date_range(filters):
    today = getdate()
    date_from = getdate(filters.get("date_from")) if filters.get("date_from") else add_days(today, -90)
    date_to = getdate(filters.get("date_to")) if filters.get("date_to") else today
    return date_from, date_to


def get_alert_days():
    try:
        value = frappe.conf.get("dds_no_dds_alert_days")
    except Exception:
        value = None
    return 3 if value is None else int(value or 0)
