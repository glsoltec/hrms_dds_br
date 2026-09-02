frappe.query_reports["DDS Dashboard"] = {
	filters: [
		{
			fieldname: "date_from",
			label: __("Data inicial"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
		},
		{
			fieldname: "date_to",
			label: __("Data final"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};
