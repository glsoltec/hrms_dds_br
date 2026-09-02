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


def ensure_dds_roles():
    if not frappe.db.exists("Role", "Responsavel DDS"):
        frappe.get_doc(
            {
                "doctype": "Role",
                "name": "Responsavel DDS",
                "desk_access": 1,
                "is_custom": 1,
            }
        ).insert(ignore_permissions=True)


def after_migrate():
    sync_employee_dds_report_roles()
    frappe.cache.delete_value("doctype_modules")
    ensure_default_topics()
    ensure_dds_roles()
    sync_dds_workspace_links()
    sync_sst_workspace_and_sidebar()


def sync_dds_workspace_links():
    workspace_name = "DDS"
    workspace = frappe.db.exists("Workspace", workspace_name)
    if not workspace:
        return

    workspace = frappe.get_doc("Workspace", workspace_name)
    shortcuts_changed = _ensure_workspace_shortcuts(workspace)
    charts_changed = _ensure_workspace_charts_and_cards(workspace)
    content_changed = _rebuild_dds_content(workspace)
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

    changed = (
        content_changed
        or shortcuts_changed
        or charts_changed
        or len(workspace.links) != len(existing_links)
    )
    changed = _ensure_workspace_roles(workspace, ["Responsavel DDS"]) or changed
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


def _normalize_workspace_content(workspace):
    original = workspace.content
    if isinstance(original, str):
        try:
            content = json.loads(original or "[]")
        except json.JSONDecodeError:
            content = []
    else:
        content = original or []
    if not isinstance(content, list):
        content = []
    workspace.content = json.dumps(content, ensure_ascii=False)
    return workspace.content != original


def _ensure_workspace_links(workspace, links):
    valid_targets = {target for _lt, target, *_rest in links}
    existing = list(workspace.links)
    workspace.links = [link for link in workspace.links if link.link_to in valid_targets]
    changed = _normalize_workspace_content(workspace) or len(workspace.links) != len(existing)
    for index, (link_type, link_to, label, is_query_report, group) in enumerate(links):
        link = next(
            (item for item in workspace.links if item.link_type == link_type and item.link_to == link_to),
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
    return changed


def _ensure_sidebar_items(sidebar, items):
    existing = list(sidebar.items)
    valid_labels = {label for label in items}
    sidebar.items = [item for item in sidebar.items if item.label in valid_labels]
    changed = len(sidebar.items) != len(existing)
    for index, (label, link_type, link_to) in enumerate(items):
        item = next(
            (i for i in sidebar.items if i.label == label),
            None,
        )
        if item is None:
            item = sidebar.append("items", {})
            changed = True
        if getattr(item, "label", None) != label:
            item.label = label
            changed = True
        if getattr(item, "link_type", None) != link_type:
            item.link_type = link_type
            changed = True
        if getattr(item, "link_to", None) != link_to:
            item.link_to = link_to
            changed = True
        if getattr(item, "type", None) != "Link":
            item.type = "Link"
            changed = True
        if item.idx != index + 1:
            item.idx = index + 1
            changed = True
    return changed


def _ensure_workspace_shortcuts(workspace):
    existing = list(workspace.shortcuts)
    valid_labels = {"DDS", "DDS Tema"}
    workspace.shortcuts = [s for s in workspace.shortcuts if s.label in valid_labels]
    changed = len(workspace.shortcuts) != len(existing)
    config = {
        "DDS": {"color": "Green", "link_to": "DDS"},
        "DDS Tema": {"color": "Blue", "link_to": "DDS Tema"},
    }
    for label, conf in config.items():
        shortcut = next((s for s in workspace.shortcuts if s.label == label), None)
        if shortcut is None:
            shortcut = workspace.append("shortcuts", {})
            changed = True
        if getattr(shortcut, "label", None) != label:
            shortcut.label = label
            changed = True
        if getattr(shortcut, "link_to", None) != conf["link_to"]:
            shortcut.link_to = conf["link_to"]
            changed = True
        if getattr(shortcut, "type", None) != "DocType":
            shortcut.type = "DocType"
            changed = True
        if getattr(shortcut, "color", None) != conf["color"]:
            shortcut.color = conf["color"]
            changed = True
        if getattr(shortcut, "doc_view", None) != "List":
            shortcut.doc_view = "List"
            changed = True
    return changed


def _rebuild_dds_content(workspace):
    shortcut_names = {
        shortcut.label: shortcut.name
        for shortcut in workspace.shortcuts
    }
    content = [
        {
            "id": "dds_header",
            "type": "header",
            "data": {"text": "<span class=\"h4\">Diálogo Diário de Segurança</span>", "col": 12},
        },
    ]
    for label, block_id in (("DDS", "dds_shortcut"), ("DDS Tema", "dds_tema_shortcut")):
        if shortcut_names.get(label):
            content.append(
                {
                    "id": block_id,
                    "type": "shortcut",
                    "data": {"shortcut_name": shortcut_names[label], "col": 4},
                }
            )
    new_content = json.dumps(content, ensure_ascii=False)
    changed = workspace.content != new_content
    workspace.content = new_content
    return changed


def _rebuild_sst_content(workspace):
    shortcut_names = {
        shortcut.label: shortcut.name
        for shortcut in workspace.shortcuts
    }
    content = [
        {
            "id": "dds_header",
            "type": "header",
            "data": {
                "text": "<span class=\"h4\">Segurança do Trabalho</span>",
                "col": 12,
            },
        },
    ]
    if shortcut_names.get("DDS"):
        content.append(
            {
                "id": "dds_shortcut",
                "type": "shortcut",
                "data": {"shortcut_name": shortcut_names["DDS"], "col": 4},
            }
        )
    if shortcut_names.get("DDS Tema"):
        content.append(
            {
                "id": "dds_tema_shortcut",
                "type": "shortcut",
                "data": {"shortcut_name": shortcut_names["DDS Tema"], "col": 4},
            }
        )
    new_content = json.dumps(content, ensure_ascii=False)
    changed = workspace.content != new_content
    workspace.content = new_content
    return changed


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


def _ensure_workspace_charts_and_cards(workspace):
    chart_names = {item.chart_name for item in workspace.charts}
    card_names = {item.number_card_name for item in workspace.number_cards}
    changed = False
    for name in ("DDS por Mês",):
        if name not in chart_names:
            workspace.append("charts", {"chart_name": name})
            changed = True
    for name in ("Total DDS", "DDS Enviados", "DDS Cancelados"):
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
    workspace = frappe.db.exists("Workspace", "Seguranca do Trabalho")
    if workspace:
        workspace = frappe.get_doc("Workspace", "Seguranca do Trabalho")
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

    sidebar = frappe.db.exists("Workspace Sidebar", "Segurança do Trabalho")
    if sidebar:
        sidebar = frappe.get_doc("Workspace Sidebar", "Segurança do Trabalho")
        items = [
            ("Home", "Workspace", "Seguranca do Trabalho"),
            ("DDS", "DocType", "DDS"),
            ("DDS Tema", "DocType", "DDS Tema"),
            ("Employee DDS History", "Report", "Employee DDS History"),
        ]
        if _ensure_sidebar_items(sidebar, items):
            sidebar.save(ignore_permissions=True)


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
