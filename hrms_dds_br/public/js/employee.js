frappe.ui.form.on("Employee", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}
		frm.add_custom_button(
			__("Histórico de DDS"),
			function () {
				frappe.set_route("query-report", "Employee DDS History", {
					employee: frm.doc.name,
				});
			},
			__("DDS"),
		);
	},
});
