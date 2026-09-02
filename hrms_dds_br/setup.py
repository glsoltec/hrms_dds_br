import frappe


WORKFLOW_STATES = {
    "Rascunho": "Warning",
    "Realizado/Enviado": "Success",
    "Cancelado": "Danger",
}
WORKFLOW_ACTIONS = ("Enviar", "Cancelar")


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


def ensure_dds_settings():
    doctype = "HRMS DDS BR Settings"
    if not frappe.db.exists("DocType", doctype) or frappe.db.exists(doctype, doctype):
        return

    settings = frappe.new_doc(doctype)
    settings.name = doctype
    settings.allow_retroactive_days = 1
    settings.allow_future_days = 0
    settings.no_dds_alert_days = 3
    settings.flags.ignore_mandatory = True
    settings.insert(ignore_permissions=True)


def inject_hrms_home_asset(response=None, request=None):
    if not response or not request or not (
        request.path == "/hrms" or request.path.startswith("/hrms/")
    ):
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
