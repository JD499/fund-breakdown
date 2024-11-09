let securityCount = 1;

function initializeFormHandlers() {
    document.getElementById('add-security').addEventListener('click', addSecurityRow);
    document.getElementById('security-inputs').addEventListener('click', handleSecurityRemoval);
    document.getElementById('portfolio-form').addEventListener('submit', handleFormSubmit);
}

function addSecurityRow() {
    securityCount++;
    const newRow = `
            <tr>
                <td><input type="text"
                           aria-label="Security Ticker ${securityCount}"
                           name="ticker"
                           placeholder="SPY"
                           required></td>
                <td><input type="number"
                           aria-label="Weight Percentage ${securityCount}"
                           name="weight"
                           min="0"
                           max="100"
                           step="0.01"
                           placeholder="100"
                           required></td>
                <td><button type="button"
                            class="remove-security"
                            aria-label="Remove Security ${securityCount}">×</button></td>
            </tr>
        `;
    document.getElementById('security-inputs').insertAdjacentHTML('beforeend', newRow);
}

function handleSecurityRemoval(event) {
    if (event.target.className === 'remove-security') {
        event.target.parentNode.parentNode.remove();
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();

    const errorElement = document.getElementById('error-message');
    const loadingElement = document.getElementById('loading');
    const resultsElement = document.getElementById('results');

    errorElement.style.display = 'none';
    loadingElement.style.display = 'block';
    resultsElement.style.display = 'none';

    try {
        const response = await fetch('/analyze', {
            method: 'POST', body: new FormData(event.target)
        });

        if (!response.ok) {
            const errorData = await response.json();
            errorElement.textContent = errorData.detail;
            errorElement.style.display = 'block';
        } else {
            const data = await response.json();
            displayHoldings(data.holdings);


            if (!window.Chart) {
                await loadChartJS();
            }
            displaySectors(data.sectors);
            resultsElement.style.display = 'grid';
        }
    } catch (error) {
        errorElement.textContent = 'An error occurred. Please try again.';
        errorElement.style.display = 'block';
    }

    loadingElement.style.display = 'none';
}

function displayHoldings(holdings) {
    document.getElementById('holdings-table').innerHTML = `
            <table aria-label="Portfolio Holdings">
                <thead>
                    <tr>
                        <th scope="col">Name</th>
                        <th scope="col">Ticker</th>
                        <th scope="col">Sector</th>
                        <th scope="col">Nation</th>
                        <th scope="col">Weight</th>
                    </tr>
                </thead>
                <tbody>
                    ${holdings.map(holding => `
                        <tr>
                            <td>${holding.Name}</td>
                            <td>${holding.Ticker}</td>
                            <td>${holding.Sector}</td>
                            <td>${holding.Nation}</td>
                            <td aria-label="Weight ${holding.Weight.toFixed(2)} percent">
                                ${holding.Weight.toFixed(2)}%
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
}

async function loadChartJS() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = '/static/chart.umd.js';
        script.onload = resolve;
        script.onerror = reject;
        document.body.appendChild(script);
    });
}

let chart = null;

function displaySectors(sectors) {
    const sectorData = Object.entries(sectors).map(([sector, weight]) => ({
        sector, weight: weight.toFixed(2)
    }));

    const ctx = document.createElement('canvas');
    ctx.id = 'sectorChart';
    ctx.setAttribute('role', 'img');
    ctx.setAttribute('aria-label', 'Sector Distribution Chart');

    const container = document.getElementById('chart-container');
    container.innerHTML = '';
    container.appendChild(ctx);

    if (chart) {
        chart.destroy();
    }

    Chart.defaults.font.family = 'Berkeley Mono';
    chart = new Chart(ctx, {
        type: 'pie', data: {
            labels: sectorData.map(data => data.sector), datasets: [{
                data: sectorData.map(data => data.weight),
                backgroundColor: ['#0366d6', '#28a745', '#6f42c1', '#f6a580', '#d79922', '#959da5', '#586069', '#2188ff', '#34d058', '#8a63d2', '#f08080']
            }]
        }, options: {
            responsive: true, maintainAspectRatio: false, plugins: {
                legend: {
                    position: window.innerWidth < 768 ? 'bottom' : 'right', labels: {
                        font: {
                            size: window.innerWidth < 768 ? 10 : 12
                        }, boxWidth: window.innerWidth < 768 ? 12 : 16, padding: window.innerWidth < 768 ? 10 : 15
                    }
                }, tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return `${label}: ${value.toFixed(2)}%`;
                        }
                    }
                }
            }
        }
    });
}


initializeFormHandlers();