import frappe
from frappe import _


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

