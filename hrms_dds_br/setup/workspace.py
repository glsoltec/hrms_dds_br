import frappe

from .content import (
    _ensure_sidebar_items,
    _ensure_workspace_links,
    _ensure_workspace_shortcuts,
    _rebuild_sst_content,
)
from .dashboard import ensure_dds_charts_and_cards


def _ensure_workspace_charts_and_cards(workspace):
    chart_names = {item.chart_name for item in workspace.charts}
    card_names = {item.number_card_name for item in workspace.number_cards}
    changed = False
    for name in (
        "DDS por Mês",
        "DDS por Tema",
        "DDS por Projeto",
        "DDS por Situação",
    ):
        if name not in chart_names:
            workspace.append("charts", {"chart_name": name})
            changed = True
    for name in ("Total DDS", "DDS Enviados", "DDS Cancelados", "DDS Rascunho"):
        if name not in card_names:
            workspace.append(
                "number_cards",
                {"number_card_name": name, "label": name},
            )
            changed = True
    return changed


def _ensure_workspace_roles(workspace, roles):
    existing = {item.role for item in workspace.roles}
    changed = False
    for role in roles:
        if role not in existing:
            workspace.append("roles", {"role": role})
            changed = True
    return changed


def sync_sst_workspace_and_sidebar():
    ensure_dds_charts_and_cards()

    old_workspace = "Seguranca do Trabalho"
    workspace_name = "SST DDS"
    if not frappe.db.exists("Workspace", workspace_name):
        if frappe.db.exists("Workspace", old_workspace):
            frappe.rename_doc("Workspace", old_workspace, workspace_name, force=True)

    if not frappe.db.exists("Workspace", workspace_name):
        created = frappe.get_doc(
            {
                "doctype": "Workspace",
                "label": "Diálogo Diário de Segurança",
                "title": "Diálogo Diário de Segurança",
                "app": "hrms_dds_br",
                "module": "HRMS DDS BR",
                "icon": "safety",
                "indicator_color": "green",
                "public": 1,
            }
        ).insert(ignore_permissions=True)
        if created.name != workspace_name:
            frappe.rename_doc("Workspace", created.name, workspace_name, force=True)

    workspace = frappe.get_doc("Workspace", workspace_name)
    workspace.label = "Diálogo Diário de Segurança"
    workspace.title = "Diálogo Diário de Segurança"
    links = [
        ("DocType", "DDS", "Registros de DDS", 0, "Cadastros"),
        ("DocType", "DDS Tema", "Temas de DDS", 0, "Cadastros"),
        ("Report", "Employee DDS History", "Histórico de DDS do Empregado", 1, "Relatórios"),
        ("Report", "DDS Dashboard", "Painel de DDS", 1, "Relatórios"),
    ]
    content_changed = _rebuild_sst_content(workspace)
    shortcuts_changed = _ensure_workspace_shortcuts(workspace)
    links_changed = _ensure_workspace_links(workspace, links)
    charts_changed = _ensure_workspace_charts_and_cards(workspace)
    roles_changed = _ensure_workspace_roles(
        workspace, ["Responsavel DDS"]
    )
    if shortcuts_changed or links_changed:
        content_changed = _rebuild_sst_content(workspace)
    if (
        content_changed
        or shortcuts_changed
        or links_changed
        or charts_changed
        or roles_changed
    ):
        workspace.save(ignore_permissions=True)

    old_sidebar = "Segurança do Trabalho"
    sidebar_name = "SST DDS"
    if not frappe.db.exists("Workspace Sidebar", sidebar_name):
        if frappe.db.exists("Workspace Sidebar", old_sidebar):
            frappe.rename_doc("Workspace Sidebar", old_sidebar, sidebar_name, force=True)
    sidebar = frappe.db.exists("Workspace Sidebar", sidebar_name)
    if sidebar:
        sidebar = frappe.get_doc("Workspace Sidebar", sidebar_name)
        items = [
            ("Home", "Workspace", workspace_name),
            ("DDS", "DocType", "DDS"),
            ("DDS Tema", "DocType", "DDS Tema"),
            ("Employee DDS History", "Report", "Employee DDS History"),
        ]
        if _ensure_sidebar_items(sidebar, items):
            sidebar.save(ignore_permissions=True)

