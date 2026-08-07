document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const investmentInput = document.getElementById('investmentAmount');
    const riskSlider = document.getElementById('riskPreference');
    const riskLabel = document.getElementById('riskLabel');
    const maxAllocSlider = document.getElementById('maxAllocation');
    const maxAllocLabel = document.getElementById('maxAllocLabel');
    const optimizeBtn = document.getElementById('optimizeBtn');
    
    const classReturnVal = document.getElementById('classReturnVal');
    const quantReturnVal = document.getElementById('quantReturnVal');
    const classSharpeVal = document.getElementById('classSharpeVal');
    const quantSharpeVal = document.getElementById('quantSharpeVal');
    
    const tableBody = document.getElementById('allocationTableBody');
    const benchmarkTableBody = document.getElementById('benchmarkTableBody');
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    const copilotSummary = document.getElementById('copilotSummary');
    const copilotInsights = document.getElementById('copilotInsights');
    
    const modal = document.getElementById('explainModal');
    const closeModal = document.querySelector('.close-modal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    let currentOptimizationResults = null;
    let activeTab = 'classical';
    let assetMetadata = [];
    let chartInstance = null;

    // Slider Listeners
    riskSlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        let text = `Balanced (${val.toFixed(2)})`;
        if (val < 0.35) text = `Low Risk (${val.toFixed(2)})`;
        if (val > 0.65) text = `High Return (${val.toFixed(2)})`;
        riskLabel.textContent = text;
    });

    maxAllocSlider.addEventListener('input', (e) => {
        maxAllocLabel.textContent = `${Math.round(e.target.value * 100)}%`;
    });

    // Tab Buttons
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeTab = btn.dataset.tab;
            if (currentOptimizationResults) {
                renderAllocationTable(currentOptimizationResults);
            }
        });
    });

    // Modal Close
    closeModal.addEventListener('click', () => modal.classList.add('hidden'));
    window.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    });

    // Load Initial Assets Universe
    fetchAssets();

    async function fetchAssets() {
        try {
            const res = await fetch('/api/assets');
            assetMetadata = await res.json();
            // Initial auto-optimize run
            runOptimization();
        } catch (err) {
            console.error('Error fetching assets:', err);
        }
    }

    // Optimize Button Action
    optimizeBtn.addEventListener('click', runOptimization);

    async function runOptimization() {
        const btnText = optimizeBtn.querySelector('.btn-text');
        const btnSpinner = optimizeBtn.querySelector('.btn-spinner');
        
        btnText.classList.add('hidden');
        btnSpinner.classList.remove('hidden');
        optimizeBtn.disabled = true;

        const payload = {
            investment_amount: parseFloat(investmentInput.value) || 1000000,
            risk_aversion: parseFloat(riskSlider.value),
            max_weight: parseFloat(maxAllocSlider.value),
            tech_cap: 0.55
        };

        try {
            const res = await fetch('/api/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            currentOptimizationResults = await res.json();
            updateUI(currentOptimizationResults);
        } catch (err) {
            console.error('Optimization error:', err);
            alert('Failed to optimize portfolio. Ensure backend is running.');
        } finally {
            btnText.classList.remove('hidden');
            btnSpinner.classList.add('hidden');
            optimizeBtn.disabled = false;
        }
    }

    function updateUI(results) {
        // Quick summary boxes
        classReturnVal.textContent = `${(results.classical.expected_return * 100).toFixed(1)}%`;
        quantReturnVal.textContent = `${(results.quantum.expected_return * 100).toFixed(1)}%`;
        classSharpeVal.textContent = results.classical.sharpe_ratio.toFixed(2);
        quantSharpeVal.textContent = results.quantum.sharpe_ratio.toFixed(2);

        // Render allocation table
        renderAllocationTable(results);

        // Render benchmark metrics table
        renderBenchmarkTable(results);

        // Render chart
        renderChart(results);

        // Co-pilot insights
        if (results.copilot_explanation) {
            copilotSummary.textContent = `"${results.copilot_explanation.summary_text}"`;
            copilotInsights.innerHTML = results.copilot_explanation.key_insights
                .map(item => `<li><i class="fa-solid fa-circle-check text-cyan"></i> ${item}</li>`)
                .join('');
        }
    }

    function renderAllocationTable(results) {
        const data = results[activeTab];
        const dollars = results.dollar_allocations[activeTab];
        const alloc = data.allocation;

        let html = '';
        assetMetadata.forEach(asset => {
            const ticker = asset.ticker;
            const weight = alloc[ticker] || 0.0;
            const capital = dollars[ticker] || 0.0;

            html += `
                <tr>
                    <td><strong>${ticker}</strong> <span style="font-size:11px; color:#94A3B8;">(${asset.name})</span></td>
                    <td><span class="badge-sector">${asset.sector}</span></td>
                    <td class="text-cyan"><strong>${(weight * 100).toFixed(1)}%</strong></td>
                    <td>₹ ${capital.toLocaleString('en-IN')}</td>
                    <td>
                        <button class="btn-explain" data-ticker="${ticker}" data-weight="${weight}">
                            Why?
                        </button>
                    </td>
                </tr>
            `;
        });

        tableBody.innerHTML = html;

        // Attach modal trigger to "Why?" buttons
        document.querySelectorAll('.btn-explain').forEach(b => {
            b.addEventListener('click', async (e) => {
                const t = e.target.dataset.ticker;
                const w = e.target.dataset.weight;
                modalTitle.innerHTML = `<i class="fa-solid fa-lightbulb text-yellow"></i> Why ${t}?`;
                modalBody.textContent = "Analyzing asset profile...";
                modal.classList.remove('hidden');

                try {
                    const res = await fetch(`/api/explain/${t}?weight=${w}`);
                    const exp = await res.json();
                    modalBody.textContent = exp.explanation;
                } catch (err) {
                    modalBody.textContent = `Asset ${t} contributes to total portfolio risk-return optimization.`;
                }
            });
        });
    }

    function renderBenchmarkTable(results) {
        let html = '';
        results.benchmarks.forEach(item => {
            html += `
                <tr>
                    <td><strong>${item.metric}</strong></td>
                    <td class="text-cyan">${item.classical}</td>
                    <td class="text-purple">${item.quantum}</td>
                </tr>
            `;
        });
        benchmarkTableBody.innerHTML = html;
    }

    function renderChart(results) {
        const tickers = Object.keys(results.classical.allocation);
        const classWeights = tickers.map(t => results.classical.allocation[t] * 100);
        const quantWeights = tickers.map(t => results.quantum.allocation[t] * 100);

        const ctx = document.getElementById('allocationChart').getContext('2d');
        if (chartInstance) chartInstance.destroy();

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: tickers,
                datasets: [
                    {
                        label: 'Classical (CVXPY)',
                        data: classWeights,
                        backgroundColor: 'rgba(0, 240, 255, 0.7)',
                        borderColor: '#00F0FF',
                        borderWidth: 1
                    },
                    {
                        label: 'Quantum (Qiskit QUBO)',
                        data: quantWeights,
                        backgroundColor: 'rgba(157, 78, 221, 0.7)',
                        borderColor: '#9D4EDD',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        ticks: { color: '#94A3B8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    },
                    y: {
                        ticks: { color: '#94A3B8', callback: v => v + '%' },
                        grid: { color: 'rgba(255, 255, 255, 0.08)' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#F0F4FC', font: { family: 'Outfit' } }
                    }
                }
            }
        });
    }
});
