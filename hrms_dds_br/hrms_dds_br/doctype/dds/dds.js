frappe.ui.form.on("DDS Participante", {
	employee(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.employee) {
			frappe.model.set_value(cdt, cdn, "designation", "");
			return;
		}

		frappe.db.get_value("Employee", row.employee, "designation").then((result) => {
			frappe.model.set_value(cdt, cdn, "designation", result.message?.designation || "");
		});
	},
});

frappe.ui.form.on("DDS", {
	is_correction(frm) {
		frm.refresh_field("correction_section");
		frm.refresh_field("original_dds");
		frm.refresh_field("correction_reason");
	},

	workflow_state(frm) {
		frm.refresh_field("cancellation_section");
		frm.refresh_field("cancellation_reason");
		frm.refresh_field("cancelled_by");
		frm.refresh_field("cancelled_at");
	},

	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.docstatus === 1 && frm.doc.workflow_state === "Realizado/Enviado") {
			if (frappe.user.has_role(["Safety Manager", "System Manager"])) {
				frm.add_custom_button(
					__("Cancelar DDS"),
					() => cancel_with_reason(frm),
					__("Ações"),
				);
			}
		}

		if (frm.doc.docstatus === 2 && frm.doc.workflow_state === "Cancelado") {
			if (frappe.user.has_role(["Safety Manager", "System Manager"])) {
				frm.add_custom_button(
					__("Criar Correção"),
					() => create_correction(frm),
					__("Ações"),
				);
			}
		}
	},

	project(frm) {
		if (!frm.doc.project) {
			frm.set_value("company", "");
			return;
		}

		frappe.db.get_value("Project", frm.doc.project, "company").then((result) => {
			frm.set_value("company", result.message?.company || "");
		});
	},

	setup(frm) {
		const active_employee_filter = () => ({ filters: { status: "Active" } });
		frm.set_query("responsible", active_employee_filter);
		frm.set_query("employee", "participants", active_employee_filter);
	},
});

function cancel_with_reason(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __("Motivo do cancelamento"),
		fields: [
			{
				fieldname: "reason",
				fieldtype: "Small Text",
				label: __("Motivo"),
				reqd: 1,
			},
		],
		primary_action_label: __("Cancelar DDS"),
		primary_action(values) {
			frappe
				.xcall("hrms_dds_br.hrms_dds_br.doctype.dds.dds.cancel_dds", {
					doc: frm.doc,
					cancellation_reason: values.reason,
				})
				.then(() => {
					frappe.show_alert({ message: __("DDS cancelado."), indicator: "green" });
					frm.reload_doc();
				})
				.catch((error) => {
					frappe.msgprint({
						title: __("Não foi possível cancelar"),
						message: error?.message || __("Erro inesperado."),
						indicator: "red",
					});
				});
			dialog.hide();
		},
	});
	dialog.show();
}

function create_correction(frm) {
	frappe.route_options = {
		is_correction: 1,
		original_dds: frm.doc.name,
		project: frm.doc.project,
		company: frm.doc.company,
		location: frm.doc.location,
		responsible: frm.doc.responsible,
		topic: frm.doc.topic,
		date: frappe.datetime.get_today(),
		participants: (frm.doc.participants || []).map((row) => ({
			employee: row.employee,
			present: 1,
		})),
	};
	frappe.new_doc("DDS");
}
