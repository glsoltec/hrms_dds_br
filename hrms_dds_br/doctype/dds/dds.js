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
	project(frm) {
		if (!frm.doc.project) {
			frm.set_value("customer", "");
			frm.set_value("company", "");
			return;
		}

		frappe.db.get_value("Project", frm.doc.project, ["customer", "company"]).then((result) => {
			frm.set_value("customer", result.message?.customer || "");
			frm.set_value("company", result.message?.company || "");
		});
	},

	setup(frm) {
		const active_employee_filter = () => ({ filters: { status: "Active" } });
		frm.set_query("responsible", active_employee_filter);
		frm.set_query("employee", "participants", active_employee_filter);
	},
});
