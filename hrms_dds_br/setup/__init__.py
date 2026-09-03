import frappe

from .asset import inject_hrms_home_asset
from .dashboard import ensure_dds_charts_and_cards
from .desktop import sync_desktop_icon_label
from .masters import (
    ensure_default_topics,
    ensure_dds_roles,
    ensure_workflow_masters,
    sync_employee_dds_report_roles,
)
from .workspace import sync_sst_workspace_and_sidebar


def after_migrate():
    sync_employee_dds_report_roles()
    frappe.cache.delete_value("doctype_modules")
    ensure_default_topics()
    ensure_dds_roles()
    ensure_dds_charts_and_cards()
    sync_desktop_icon_label()
    sync_sst_workspace_and_sidebar()
