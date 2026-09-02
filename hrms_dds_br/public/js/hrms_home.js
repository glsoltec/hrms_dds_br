(function () {
	"use strict";

	const reportUrl = "/desk/query-report/Employee%20DDS%20History";
	const marker = "data-hrms-dds-link";

	function addDdsLink() {
		if (document.querySelector(`[${marker}]`)) {
			return true;
		}

		const existingLink = document.querySelector('a[href*="/hrms/attendance-requests"]');
		const quickLinks = existingLink?.closest(".flex.flex-col.gap-5.my-4.w-full");
		const linksContainer = quickLinks?.querySelector(":scope > div:nth-child(2)");
		if (!linksContainer) {
			return false;
		}

		const link = document.createElement("a");
		link.href = reportUrl;
		link.className = "flex flex-row flex-start p-4 items-center justify-between";
		link.setAttribute(marker, "1");
		link.setAttribute("aria-label", "Histórico de DDS");
		link.innerHTML =
			'<div class="flex flex-row items-center gap-3 grow">' +
			'<span class="h-5 w-5 text-gray-500 text-xs font-semibold">DDS</span>' +
			'<div class="text-base font-normal text-gray-800">Histórico de DDS</div>' +
			"</div>" +
			'<span class="h-5 w-5 text-gray-500">›</span>';
		linksContainer.appendChild(link);
		return true;
	}

	function start() {
		if (addDdsLink()) {
			return;
		}

		const observer = new MutationObserver(() => {
			if (addDdsLink()) {
				observer.disconnect();
			}
		});
		observer.observe(document.getElementById("app") || document.body, {
			childList: true,
			subtree: true,
		});
		window.setTimeout(() => observer.disconnect(), 10000);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", start, { once: true });
	} else {
		start();
	}
})();
