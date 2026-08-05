import frappe
from frappe.tests.utils import FrappeTestCase

from sst_dds_br.sst_dds_br.doctype.dds.dds import signature_digest


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
