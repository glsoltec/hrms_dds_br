frappe.ready(() => {
	const route = frappe.router?.current_route;
	if (Array.isArray(route) && route.length === 1 && route[0] === "dds") {
		window.location.replace("/app/dds");
	}
});
