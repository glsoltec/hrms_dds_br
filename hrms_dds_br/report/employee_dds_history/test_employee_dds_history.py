import frappe
from frappe.tests.utils import FrappeTestCase

from hrms_dds_br.report.employee_dds_history.employee_dds_history import (
    get_columns,
    validate_filters,
)


class TestEmployeeDDSHistory(FrappeTestCase):
    def test_get_columns_returns_expected_columns(self):
        columns = get_columns()
        fieldnames = [c["fieldname"] for c in columns]
        self.assertIn("name", fieldnames)
        self.assertIn("date", fieldnames)
        self.assertIn("employee", fieldnames)
        self.assertIn("present", fieldnames)
        self.assertIn("signed", fieldnames)

    def test_privileged_user_can_query_any_employee(self):
        original_get_roles = frappe.get_roles
        try:
            frappe.get_roles = lambda user: ["Safety Manager"]
            validate_filters({"employee": "EMP-QUALQUER"})
        finally:
            frappe.get_roles = original_get_roles

    def test_non_privileged_user_blocked_from_other_employee(self):
        original_get_roles = frappe.get_roles
        original_get_all = frappe.get_all
        try:
            frappe.get_roles = lambda user: ["Employee"]
            frappe.get_all = lambda *args, **kwargs: []
            with self.assertRaises(frappe.PermissionError):
                validate_filters({"employee": "EMP-OUTRO"})
        finally:
            frappe.get_roles = original_get_roles
            frappe.get_all = original_get_all