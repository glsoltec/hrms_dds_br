import frappe


PRIVILEGED_ROLES = {
    "System Manager",
    "HR Manager",
    "Safety Manager",
    "Safety Supervisor",
}


def dds_query_conditions(user=None):
    user = user or frappe.session.user
    roles = set(frappe.get_roles(user))
    if roles & PRIVILEGED_ROLES:
        return ""

    employees = frappe.get_all(
        "Employee",
        filters={"user_id": user, "status": "Active"},
        pluck="name",
    )
    if not employees:
        return "1=0"

    employee_list = ", ".join(frappe.db.escape(employee) for employee in employees)
    return (
        "exists (select 1 from `tabDDS Participante` participant "
        "where participant.parent = `tabDDS`.name "
        "and participant.parenttype = 'DDS' "
        f"and participant.employee in ({employee_list}))"
    )


def dds_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    roles = set(frappe.get_roles(user))
    if roles & PRIVILEGED_ROLES:
        return None

    if permission_type not in (None, "read", "print"):
        return False

    employees = set(
        frappe.get_all(
            "Employee",
            filters={"user_id": user, "status": "Active"},
            pluck="name",
        )
    )
    return any(row.employee in employees for row in doc.participants)
