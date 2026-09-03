import frappe


def sync_desktop_icon_label():
    icon = frappe.db.exists("Desktop Icon", "HRMS DDS BR")
    if not icon:
        return
    app = frappe.db.get_value("Desktop Icon", "HRMS DDS BR", "app")
    if app == "hrms_dds_br":
        frappe.db.set_value("Desktop Icon", "HRMS DDS BR", "label", "DDS")
        frappe.db.set_value(
            "Desktop Icon", "HRMS DDS BR", "link", "/desk/sst-dds"
        )

