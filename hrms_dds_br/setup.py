import json

import frappe


WORKFLOW_STATES = {
    "Rascunho": "Warning",
    "Realizado/Enviado": "Success",
    "Cancelado": "Danger",
}
WORKFLOW_ACTIONS = ("Enviar", "Cancelar")
DEFAULT_DDS_TOPICS = (
    "Trabalho em Altura",
    "Eletricidade",
    "EPI",
    "Ferramentas Manuais",
    "Máquinas e Equipamentos",
    "Produtos Químicos",
    "Ergonomia",
    "Organização e Limpeza",
    "Trânsito Interno",
    "Quase Acidentes",
    "Outro",
)


def ensure_workflow_masters():
    for state_name, style in WORKFLOW_STATES.items():
        if not frappe.db.exists("Workflow State", state_name):
            frappe.get_doc(
                {
                    "doctype": "Workflow State",
                    "workflow_state_name": state_name,
                    "style": style,
                }
            ).insert(ignore_permissions=True)

    for action_name in WORKFLOW_ACTIONS:
        if not frappe.db.exists("Workflow Action Master", action_name):
            frappe.get_doc(
                {
                    "doctype": "Workflow Action Master",
                    "workflow_action_name": action_name,
                }
            ).insert(ignore_permissions=True)


def sync_employee_dds_report_roles():
    report = frappe.db.exists("Report", "Employee DDS History")
    if not report:
        return

    report = frappe.get_doc("Report", "Employee DDS History")
    roles = {row.role for row in report.roles}
    changed = False
    for role in ("Employee", "Employee Self Service"):
        if role not in roles:
            report.append("roles", {"role": role})
            changed = True
    if changed:
        report.save(ignore_permissions=True)


def ensure_default_topics():
    for sort_order, topic in enumerate(DEFAULT_DDS_TOPICS, start=1):
        if not frappe.db.exists("DDS Tema", topic):
            frappe.get_doc(
                {
                    "doctype": "DDS Tema",
                    "tema": topic,
                    "active": 1,
                    "sort_order": sort_order,
                }
            ).insert(ignore_permissions=True)


def after_migrate():
    sync_employee_dds_report_roles()
    frappe.cache.delete_value("doctype_modules")
    ensure_default_topics()
    sync_dds_workspace_links()


def sync_dds_workspace_links():
    workspace_name = "DDS"
    workspace = frappe.db.exists("Workspace", workspace_name)
    if not workspace:
        return

    workspace = frappe.get_doc("Workspace", workspace_name)
    content_changed = False
    if isinstance(workspace.content, str):
        try:
            workspace.content = json.loads(workspace.content or "[]")
        except json.JSONDecodeError:
            workspace.content = []
        content_changed = True
    if not isinstance(workspace.content, list):
        workspace.content = []
        content_changed = True
    valid_targets = {"DDS", "DDS Tema", "Employee DDS History", "DDS Dashboard"}
    existing_links = list(workspace.links)
    workspace.links = [
        link
        for link in workspace.links
        if link.link_to in valid_targets
    ]
    links = [
        ("DocType", "DDS", "Registros de DDS", 0, "Cadastros"),
        ("DocType", "DDS Tema", "Temas de DDS", 0, "Cadastros"),
        ("Report", "Employee DDS History", "Histórico de DDS do Empregado", 1, "Relatórios"),
        ("Report", "DDS Dashboard", "Painel de DDS", 1, "Relatórios"),
    ]

    changed = content_changed or len(workspace.links) != len(existing_links)
    for index, (link_type, link_to, label, is_query_report, group) in enumerate(links):
        link = next(
            (
                item
                for item in workspace.links
                if item.link_type == link_type and item.link_to == link_to
            ),
            None,
        )
        if link is None:
            link = workspace.append("links", {})
            changed = True
        values = {
            "link_type": link_type,
            "link_to": link_to,
            "label": label,
            "is_query_report": is_query_report,
            "group": group,
            "hidden": 0,
            "onboard": 0,
        }
        for field, value in values.items():
            if getattr(link, field, None) != value:
                setattr(link, field, value)
                changed = True
        if link.idx != index + 1:
            link.idx = index + 1
            changed = True

    if changed:
        workspace.save(ignore_permissions=True)


def inject_hrms_home_asset(response=None, request=None):
    if not response or not request or request.path not in ("/hrms", "/hrms/", "/hrms/home"):
        return

    content_type = response.headers.get("Content-Type", "")
    if not content_type.startswith("text/html"):
        return

    marker = '<script defer src="/assets/hrms_dds_br/js/hrms_home.js"></script>'
    body = response.get_data(as_text=True)
    if marker in body or "</head>" not in body:
        return

    response.set_data(body.replace("</head>", f"{marker}</head>", 1))
    response.headers.pop("Content-Length", None)
