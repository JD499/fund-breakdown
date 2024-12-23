document
	.getElementById("portfolio-form")
	.addEventListener("submit", async function (e) {
		const submitter = e.submitter;

		e.preventDefault();

		const action = submitter.getAttribute("formaction");

		if (action === "/analyze") {
			const formData = new FormData(this);

			try {
				const errorElement = document.getElementById("error-message");
				const loadingElement = document.getElementById("loading");
				const resultsElement = document.getElementById("results");

				errorElement.style.display = "none";
				loadingElement.style.display = "block";
				resultsElement.style.display = "none";

				const response = await fetch("/analyze", {
					method: "POST",
					body: formData,
				});

				if (!response.ok) {
					const errorText = await response.text();
					errorElement.textContent = "Analysis failed. Please try again.";
					errorElement.style.display = "block";
				} else {
					const html = await response.text();
					resultsElement.innerHTML = html;

					if (!window.Chart) {
						await loadChartJS();
					}

					const sectorData = {};
					document.querySelectorAll("#sector-table tr").forEach((row) => {
						const sector = row.querySelector("td:first-child").textContent;
						const weight = Number.parseFloat(
							row.querySelector("td:last-child").textContent,
						);
						sectorData[sector] = weight;
					});

					displaySectors(sectorData);
					resultsElement.style.display = "block";
				}

				loadingElement.style.display = "none";
			} catch (error) {
				const errorMessage = document.getElementById("error-message");
				errorMessage.textContent = "An error occurred. Please try again.";
				errorMessage.style.display = "block";
				document.getElementById("loading").style.display = "none";
			}
		} else {
			await updateTable(action);
		}
	});

async function updateTable(action) {
	try {
		const form = document.getElementById("portfolio-form");
		const formData = new FormData(form);

		const response = await fetch(action, {
			method: "POST",
			body: formData,
		});

		if (!response.ok) {
			const errorText = await response.text();

			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const html = await response.text();
		document.getElementById("security-inputs").innerHTML = html;
	} catch (error) {
		const errorMessage = document.getElementById("error-message");
		if (errorMessage) {
			errorMessage.textContent = "An error occurred. Please try again.";
			errorMessage.style.display = "block";
			setTimeout(() => {
				errorMessage.style.display = "none";
			}, 3000);
		}
	}
}

async function loadChartJS() {
	return new Promise((resolve, reject) => {
		const script = document.createElement("script");
		script.src = "/static/chart.umd.js";
		script.onload = resolve;
		script.onerror = reject;
		document.body.appendChild(script);
	});
}

let chart = null;

function displaySectors(sectors) {
	const sectorData = Object.entries(sectors).map(([sector, weight]) => ({
		sector,
		weight: Number.parseFloat(weight),
	}));

	const ctx = document.createElement("canvas");
	ctx.id = "sectorChart";
	ctx.setAttribute("role", "img");
	ctx.setAttribute("aria-label", "Sector Distribution Chart");

	const container = document.getElementById("chart-container");
	container.innerHTML = "";
	container.appendChild(ctx);

	if (chart) {
		chart.destroy();
	}

	Chart.defaults.font.family = "Berkeley Mono";
	chart = new Chart(ctx, {
		type: "pie",
		data: {
			labels: sectorData.map((data) => data.sector),
			datasets: [
				{
					data: sectorData.map((data) => data.weight),
					backgroundColor: [
						"#0366d6",
						"#28a745",
						"#6f42c1",
						"#f6a580",
						"#d79922",
						"#959da5",
						"#586069",
						"#2188ff",
						"#34d058",
						"#8a63d2",
						"#f08080",
					],
				},
			],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: {
					position: window.innerWidth < 768 ? "bottom" : "right",
					labels: {
						font: {
							size: window.innerWidth < 768 ? 10 : 12,
						},
						boxWidth: window.innerWidth < 768 ? 12 : 16,
						padding: window.innerWidth < 768 ? 10 : 15,
					},
				},
				tooltip: {
					callbacks: {
						label: (context) => {
							const label = context.label || "";
							const value = context.parsed || 0;
							return `${label}: ${value.toFixed(2)}%`;
						},
					},
				},
			},
		},
	});
}
