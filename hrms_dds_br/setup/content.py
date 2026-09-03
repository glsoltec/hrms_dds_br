import json

import frappe
from frappe import _


import json

import frappe
from frappe import _


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
    content_changed = _normalize_workspace_content(workspace)
    changed = content_changed
    for index, (link_type, link_to, label, is_query_report, group) in enumerate(links):
        matches = [
            item
            for item in workspace.links
            if item.link_type == link_type and item.link_to == link_to
        ]
        link = matches[0] if matches else None
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
        for extra in matches[1:]:
            workspace.links.remove(extra)
            changed = True
    return changed


def _ensure_sidebar_items(sidebar, items):
    changed = False
    for index, (label, link_type, link_to) in enumerate(items):
        matches = [item for item in sidebar.items if item.label == label]
        item = matches[0] if matches else None
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
        for extra in matches[1:]:
            sidebar.items.remove(extra)
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


def _dashboard_blocks():
    return [
        {
            "id": "dds_chart_month",
            "type": "chart",
            "data": {"chart_name": "DDS por Mês", "col": 12},
        },
        {
            "id": "dds_card_total",
            "type": "number_card",
            "data": {"number_card_name": "Total DDS", "col": 3},
        },
        {
            "id": "dds_card_submitted",
            "type": "number_card",
            "data": {"number_card_name": "DDS Enviados", "col": 3},
        },
        {
            "id": "dds_card_cancelled",
            "type": "number_card",
            "data": {"number_card_name": "DDS Cancelados", "col": 3},
        },
        {
            "id": "dds_card_draft",
            "type": "number_card",
            "data": {"number_card_name": "DDS Rascunho", "col": 3},
        },
        {
            "id": "dds_chart_topic",
            "type": "chart",
            "data": {"chart_name": "DDS por Tema", "col": 6},
        },
        {
            "id": "dds_chart_status",
            "type": "chart",
            "data": {"chart_name": "DDS por Situação", "col": 6},
        },
        {
            "id": "dds_chart_project",
            "type": "chart",
            "data": {"chart_name": "DDS por Projeto", "col": 12},
        },
    ]


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
                "text": "<span class=\"h4\">Diálogo Diário de Segurança</span>",
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
    content.extend(_dashboard_blocks())
    new_content = json.dumps(content, ensure_ascii=False)
    changed = workspace.content != new_content
    workspace.content = new_content
    return changed
