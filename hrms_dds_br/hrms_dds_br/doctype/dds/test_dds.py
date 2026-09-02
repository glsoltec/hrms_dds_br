import frappe
from frappe.tests.utils import FrappeTestCase

from hrms_dds_br.hrms_dds_br.doctype.dds.dds import signature_digest
from hrms_dds_br.permissions import dds_has_permission


class TestDDS(FrappeTestCase):
    def test_signature_digest_is_stable(self):
        self.assertEqual(signature_digest("assinatura"), signature_digest("assinatura"))
        self.assertNotEqual(signature_digest("assinatura"), signature_digest("outra"))

    def test_duplicate_participant_is_rejected(self):
        doc = frappe.new_doc("DDS")
        doc.append("participants", {"employee": "EMP-TEST"})
        doc.append("participants", {"employee": "EMP-TEST"})

        with self.assertRaises(frappe.ValidationError):
            doc._validate_participants()

    def test_present_participant_requires_signature(self):
        doc = frappe.new_doc("DDS")
        doc.responsible_confirmation = 1
        doc.responsible_signature = "data:image/svg+xml,test"
        doc.append("participants", {"employee": "EMP-TEST", "present": 1})

        with self.assertRaises(frappe.ValidationError):
            doc._validate_completion()

    def test_signature_metadata_cannot_change_without_signature_change(self):
        doc = frappe.new_doc("DDS")
        previous = frappe.new_doc("DDS")
        previous.name = "DDS-TEST"
        previous.responsible_signature = "responsible-signature"
        previous.responsible_signature_collected_by = "collector@example.com"
        previous.responsible_signature_collected_at = "2026-08-04 10:00:00"
        previous.responsible_signature_hash = signature_digest(previous.responsible_signature)
        doc.responsible_signature = previous.responsible_signature
        doc.responsible_signature_collected_by = "other@example.com"
        doc.responsible_signature_collected_at = previous.responsible_signature_collected_at
        doc.responsible_signature_hash = previous.responsible_signature_hash
        doc.get_doc_before_save = lambda: previous

        with self.assertRaises(frappe.ValidationError):
            doc._validate_signature_evidence()

    def test_responsible_employee_has_read_permission(self):
        doc = frappe.new_doc("DDS")
        doc.responsible = "EMP-TEST"
        doc.participants = []

        original_get_roles = frappe.get_roles
        original_get_all = frappe.get_all
        try:
            frappe.get_roles = lambda user: ["Employee"]
            frappe.get_all = lambda *args, **kwargs: ["EMP-TEST"]
            self.assertTrue(dds_has_permission(doc, "test@example.com", "read"))
        finally:
            frappe.get_roles = original_get_roles
            frappe.get_all = original_get_all
