import frappe


def _ensure_dashboard_chart(name, doc):
    if not frappe.db.exists("Dashboard Chart", name):
        frappe.get_doc(doc).insert(ignore_permissions=True)


def _ensure_number_card(name, doc):
    if not frappe.db.exists("Number Card", name):
        frappe.get_doc(doc).insert(ignore_permissions=True)


def ensure_dds_charts_and_cards():
    _ensure_number_card(
        "Total DDS",
        {
            "doctype": "Number Card",
            "name": "Total DDS",
            "label": "Total DDS",
            "type": "Document Type",
            "document_type": "DDS",
            "function": "Count",
            "filters_json": "[]",
            "stats_time_interval": "Daily",
            "is_public": 1,
            "module": "HRMS DDS BR",
        },
    )
    _ensure_number_card(
        "DDS Enviados",
        {
            "doctype": "Number Card",
            "name": "DDS Enviados",
            "label": "DDS Enviados",
            "type": "Document Type",
            "document_type": "DDS",
            "function": "Count",
            "filters_json": '[["workflow_state","=","Realizado/Enviado"]]',
            "stats_time_interval": "Daily",
            "is_public": 1,
            "module": "HRMS DDS BR",
        },
    )
    _ensure_number_card(
        "DDS Cancelados",
        {
            "doctype": "Number Card",
            "name": "DDS Cancelados",
            "label": "DDS Cancelados",
            "type": "Document Type",
            "document_type": "DDS",
            "function": "Count",
            "filters_json": '[["workflow_state","=","Cancelado"]]',
            "stats_time_interval": "Daily",
            "is_public": 1,
            "module": "HRMS DDS BR",
        },
    )
    _ensure_number_card(
        "DDS Rascunho",
        {
            "doctype": "Number Card",
            "name": "DDS Rascunho",
            "label": "DDS Rascunho",
            "type": "Document Type",
            "document_type": "DDS",
            "function": "Count",
            "filters_json": '[["workflow_state","=","Rascunho"]]',
            "stats_time_interval": "Daily",
            "is_public": 1,
            "module": "HRMS DDS BR",
        },
    )
    _ensure_dashboard_chart(
        "DDS por Mês",
        {
            "doctype": "Dashboard Chart",
            "name": "DDS por Mês",
            "chart_name": "DDS por Mês",
            "chart_type": "Count",
            "document_type": "DDS",
            "based_on": "creation",
            "timeseries": 1,
            "time_interval": "Monthly",
            "timespan": "Last Year",
            "type": "Bar",
            "filters_json": "[]",
            "is_public": 1,
            "module": "HRMS DDS BR",
        },
    )
    _ensure_dashboard_chart(
        "DDS por Tema",
        {
            "doctype": "Dashboard Chart",
            "name": "DDS por Tema",
            "chart_name": "DDS por Tema",
            "chart_type": "Group By",
            "document_type": "DDS",
            "group_by_type": "Count",
            "group_by_based_on": "topic",
            "type": "Donut",
            "filters_json": "[]",
            "is_public": 1,
            "module": "HRMS DDS BR",
        },
    )
    _ensure_dashboard_chart(
        "DDS por Projeto",
        {
            "doctype": "Dashboard Chart",
            "name": "DDS por Projeto",
            "chart_name": "DDS por Projeto",
            "chart_type": "Group By",
            "document_type": "DDS",
            "group_by_type": "Count",
            "group_by_based_on": "project",
            "type": "Bar",
            "filters_json": "[]",
            "is_public": 1,
            "module": "HRMS DDS BR",
        },
    )
    _ensure_dashboard_chart(
        "DDS por Situação",
        {
            "doctype": "Dashboard Chart",
            "name": "DDS por Situação",
            "chart_name": "DDS por Situação",
            "chart_type": "Group By",
            "document_type": "DDS",
            "group_by_type": "Count",
            "group_by_based_on": "workflow_state",
            "type": "Donut",
            "filters_json": "[]",
            "is_public": 1,
            "module": "HRMS DDS BR",
        },
    )

