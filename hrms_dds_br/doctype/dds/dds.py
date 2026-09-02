from hashlib import sha256

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class DDS(Document):
    def validate(self):
        self._set_project_data()
        self._validate_employees()
        self._fill_employee_designations()
        self._record_signature_evidence()
        self._validate_signature_evidence()
        self._validate_participants()

        if self.workflow_state == "Realizado/Enviado":
            self._validate_completion()

    def before_submit(self):
        self._validate_completion()

    def _fill_employee_designations(self):
        employees = {row.employee for row in self.participants if row.employee}
        designations = dict(
            frappe.get_all(
                "Employee",
                filters={"name": ["in", list(employees)]},
                fields=["name", "designation"],
                as_list=True,
            )
        ) if employees else {}
        for row in self.participants:
            if row.employee:
                row.designation = designations.get(row.employee) or ""

    def _set_project_data(self):
        project = frappe.db.get_value(
            "Project", self.project, ["customer", "company"], as_dict=True
        )
        if not project:
            frappe.throw(_("O projeto/obra informado não existe."))

        if project.customer:
            if self.customer and self.customer != project.customer:
                frappe.throw(_("O cliente deve ser o mesmo cadastrado no projeto/obra."))
            self.customer = project.customer
        elif not self.customer:
            frappe.throw(_("Informe o cliente, pois o projeto/obra não possui cliente cadastrado."))

        if self.company and project.company and self.company != project.company:
            frappe.throw(_("A empresa deve ser a mesma cadastrada no projeto/obra."))
        self.company = project.company

    def _validate_employees(self):
        employee_names = {row.employee for row in self.participants if row.employee}
        if self.responsible:
            employee_names.add(self.responsible)
        if not employee_names:
            return

        employee_rows = frappe.get_all(
            "Employee",
            filters={"name": ["in", list(employee_names)]},
            fields=["name", "status", "company"],
        )
        employees = {row.name: row for row in employee_rows}

        for employee_name in employee_names:
            employee = employees.get(employee_name)
            if not employee:
                frappe.throw(_("O colaborador {0} não existe.").format(employee_name))
            if employee.status != "Active":
                frappe.throw(_("O colaborador {0} não está ativo.").format(employee_name))
            if self.company and employee.company != self.company:
                frappe.throw(
                    _("O colaborador {0} pertence a outra empresa.").format(employee_name)
                )

    def _record_signature_evidence(self):
        previous = self.get_doc_before_save()
        previous_rows = {
            row.name: row for row in previous.participants
        } if previous else {}

        for row in self.participants:
            old_signature = getattr(previous_rows.get(row.name), "signature", None)
            if row.signature and row.signature != old_signature:
                row.signature_collected_by = frappe.session.user
                row.signature_collected_at = now_datetime()
                row.signature_hash = signature_digest(row.signature)
            elif not row.signature:
                row.signature_collected_by = None
                row.signature_collected_at = None
                row.signature_hash = None

        old_responsible_signature = (
            previous.responsible_signature if previous else None
        )
        if self.responsible_signature and self.responsible_signature != old_responsible_signature:
            self.responsible_signature_collected_by = frappe.session.user
            self.responsible_signature_collected_at = now_datetime()
            self.responsible_signature_hash = signature_digest(self.responsible_signature)
        elif not self.responsible_signature:
            self.responsible_signature_collected_by = None
            self.responsible_signature_collected_at = None
            self.responsible_signature_hash = None

    def _validate_signature_evidence(self):
        previous = self.get_doc_before_save()
        if not previous:
            return

        previous_rows = {row.name: row for row in previous.participants}
        metadata_fields = (
            "signature_collected_by",
            "signature_collected_at",
            "signature_hash",
        )
        for row in self.participants:
            old_row = previous_rows.get(row.name)
            if not old_row or row.signature != old_row.signature:
                continue
            if any(getattr(row, field) != getattr(old_row, field) for field in metadata_fields):
                frappe.throw(_("Os metadados da assinatura do participante não podem ser alterados."))

        responsible_fields = (
            "responsible_signature_collected_by",
            "responsible_signature_collected_at",
            "responsible_signature_hash",
        )
        if self.responsible_signature == previous.responsible_signature and any(
            getattr(self, field) != getattr(previous, field) for field in responsible_fields
        ):
            frappe.throw(_("Os metadados da assinatura do responsável não podem ser alterados."))

    def _validate_participants(self):
        seen = set()
        for row in self.participants:
            if not row.employee:
                frappe.throw(_("Informe o colaborador na linha {0}.").format(row.idx))
            if row.employee in seen:
                frappe.throw(_("O colaborador {0} foi incluído mais de uma vez.").format(row.employee))
            seen.add(row.employee)

    def _validate_completion(self):
        if not self.responsible_confirmation:
            frappe.throw(_("O responsável deve confirmar a realização do DDS."))
        if not self.responsible_signature:
            frappe.throw(_("A assinatura do responsável é obrigatória."))
        if not self.participants:
            frappe.throw(_("Inclua ao menos um participante."))

        for row in self.participants:
            if row.present and not row.signature:
                frappe.throw(
                    _("A assinatura do participante {0} é obrigatória.").format(row.employee)
                )


def signature_digest(signature):
    return sha256(signature.encode("utf-8")).hexdigest()
