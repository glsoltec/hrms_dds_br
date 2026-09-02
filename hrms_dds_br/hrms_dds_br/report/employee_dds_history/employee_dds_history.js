frappe.query_reports["Employee DDS History"] = {
	filters: [
		{
			fieldname: "employee",
			label: __("Empregado"),
			fieldtype: "Link",
			options: "Employee",
		},
	],
};
