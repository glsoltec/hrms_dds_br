from hashlib import sha256

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, now_datetime

from hrms_dds_br.permissions import PRIVILEGED_ROLES


def signature_digest(signature):
    return sha256(signature.encode("utf-8")).hexdigest()


class DDS(Document):
    def validate(self):
        self._set_project_data()
        self._validate_employees()
        self._validate_submitted_immutability()
        self._validate_correction_fields()
        self._validate_date_range()
        self._fill_employee_designations()
        self._record_signature_evidence()
        self._validate_signature_evidence()
        self._validate_participants()

        if self.workflow_state == "Realizado/Enviado":
            self._validate_completion()

    def before_submit(self):
        self._validate_completion()

    def before_cancel(self):
        if not self.cancellation_reason or not self.cancellation_reason.strip():
            frappe.throw(_("Informe o motivo do cancelamento antes de cancelar o DDS."))
        self.cancellation_reason = self.cancellation_reason.strip()
        self.cancelled_by = frappe.session.user
        self.cancelled_at = now_datetime()

    def on_trash(self):
        if self.docstatus != 0:
            frappe.throw(
                _("Não é possível excluir fisicamente um DDS enviado ou cancelado. Use o cancelamento formal.")
            )

    def onload(self):
        if self._is_privileged_access():
            return
        own_employees = self._get_user_employees()
        if self.responsible_signature and self.responsible not in own_employees:
            self.responsible_signature = None
        for row in self.participants:
            if row.signature and row.employee not in own_employees:
                row.signature = None

    def _is_privileged_access(self):
        return bool(set(frappe.get_roles()) & PRIVILEGED_ROLES)

    def _get_user_employees(self):
        return set(
            frappe.get_all(
                "Employee",
                filters={"user_id": frappe.session.user, "status": "Active"},
                pluck="name",
            )
        )

    def _settings_value(self, fieldname, default):
        config_map = {
            "allow_retroactive_days": "dds_retroactive_days",
            "allow_future_days": "dds_future_days",
        }
        value = frappe.conf.get(config_map.get(fieldname))
        return default if value is None else int(value)

    def _validate_date_range(self):
        if self.docstatus or not self.date:
            return
        retroactive_days = int(self._settings_value("allow_retroactive_days", 1) or 0)
        future_days = int(self._settings_value("allow_future_days", 0) or 0)
        today = getdate()
        if getdate(self.date) < add_days(today, -retroactive_days):
            frappe.throw(
                _("A data do DDS não pode ser retroativa além de {0} dia(s).").format(retroactive_days)
            )
        if getdate(self.date) > add_days(today, future_days):
            frappe.throw(
                _("A data do DDS não pode ser futura além de {0} dia(s).").format(future_days)
            )

    def _validate_correction_fields(self):
        if self.original_dds and not self.is_correction:
            frappe.throw(_("Marque 'É correção de um DDS anterior' ao informar o DDS original."))
        if self.is_correction and not self.original_dds:
            frappe.throw(_("Informe o DDS original que está sendo corrigido."))
        if self.is_correction and not self.correction_reason:
            frappe.throw(_("Informe o motivo da correção."))

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
        project = frappe.db.get_value("Project", self.project, ["customer", "company"], as_dict=True)
        if not project:
            frappe.throw(_("O projeto/obra informado não existe."))

        if not project.customer:
            frappe.throw(_("O projeto/obra deve possuir um cliente cadastrado."))

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

    def _validate_submitted_immutability(self):
        previous = self.get_doc_before_save()
        if not previous or previous.docstatus != 1 or self.docstatus == 2:
            return

        immutable_fields = (
            "date",
            "time",
            "project",
            "company",
            "location",
            "responsible",
            "topic",
            "objective",
            "risks_addressed",
            "preventive_measures",
            "observations",
            "responsible_confirmation",
            "responsible_signature",
            "responsible_signature_collected_by",
            "responsible_signature_collected_at",
            "responsible_signature_hash",
            "photo",
        )
        if any(getattr(self, field) != getattr(previous, field) for field in immutable_fields):
            frappe.throw(_("Um DDS enviado não pode ser alterado. Cancele-o e registre um novo DDS."))

        participant_fields = (
            "employee",
            "designation",
            "present",
            "signature",
            "signature_collected_by",
            "signature_collected_at",
            "signature_hash",
            "observation",
        )
        current_participants = [
            tuple(getattr(row, field) for field in participant_fields)
            for row in self.participants
        ]
        previous_participants = [
            tuple(getattr(row, field) for field in participant_fields)
            for row in previous.participants
        ]
        if current_participants != previous_participants:
            frappe.throw(_("Os participantes de um DDS enviado não podem ser alterados."))

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


@frappe.whitelist()
def cancel_dds(doc, cancellation_reason):
    reason = (cancellation_reason or "").strip()
    if not reason:
        frappe.throw(_("Informe o motivo do cancelamento."))

    doc = frappe.get_doc(frappe.parse_json(doc))
    doc.load_from_db()
    doc.cancellation_reason = reason
    doc.db_set(
        {
            "cancellation_reason": reason,
            "cancelled_by": frappe.session.user,
            "cancelled_at": now_datetime(),
        }
    )

    from frappe.model.workflow import apply_workflow

    return apply_workflow(doc, "Cancelar")
