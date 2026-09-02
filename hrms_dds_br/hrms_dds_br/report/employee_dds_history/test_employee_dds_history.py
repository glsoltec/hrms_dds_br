import frappe
from frappe.tests.utils import FrappeTestCase

from hrms_dds_br.hrms_dds_br.report.employee_dds_history.employee_dds_history import (
    get_columns,
    select_matches,
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

    def test_select_matches_includes_responsible_for_self_service(self):
        dds = {"name": "DDS-1", "responsible": "EMP-RESP"}
        participants = [{"employee": "EMP-PART", "present": 1, "signed": 1}]
        matches = select_matches(dds, participants, None, False, {"EMP-RESP", "EMP-PART"})
        employees = {m["employee"] for m in matches}
        self.assertIn("EMP-RESP", employees)
        self.assertIn("EMP-PART", employees)

    def test_select_matches_excludes_non_own_participants(self):
        dds = {"name": "DDS-1", "responsible": "EMP-RESP"}
        participants = [
            {"employee": "EMP-PART", "present": 1, "signed": 1},
            {"employee": "EMP-OUTRO", "present": 1, "signed": 1},
        ]
        matches = select_matches(dds, participants, None, False, {"EMP-RESP", "EMP-PART"})
        employees = {m["employee"] for m in matches}
        self.assertIn("EMP-PART", employees)
        self.assertNotIn("EMP-OUTRO", employees)