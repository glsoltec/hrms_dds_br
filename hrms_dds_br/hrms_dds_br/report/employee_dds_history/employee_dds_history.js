frappe.query_reports["Employee DDS History"] = {
	filters: [
		{
			fieldname: "employee",
			label: __("Empregado"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "date_from",
			label: __("Data inicial"),
			fieldtype: "Date",
		},
		{
			fieldname: "date_to",
			label: __("Data final"),
			fieldtype: "Date",
		},
		{
			fieldname: "project",
			label: __("Projeto/Obra"),
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "topic",
			label: __("Tema"),
			fieldtype: "Link",
			options: "DDS Tema",
		},
		{
			fieldname: "workflow_state",
			label: __("Situação"),
			fieldtype: "Select",
			options: ["", "Rascunho", "Realizado/Enviado", "Cancelado"].join("\n"),
		},
	],
};
