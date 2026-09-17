fetch('/api/dash/fat-ultimos-meses').then(res => res.json()).then(data => {
    new Chart(document.getElementById('graficoFaturacao'), {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Facturação Mensal (€)',
                data: data.valores,
                backgroundColor: 'rgba(99, 102, 241, 0.4)', // brand-500
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
});

fetch('/api/dash/os-status').then(res => res.json()).then(data => {
    new Chart(document.getElementById('graficoOsStatus'), {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.valores,
                backgroundColor: [
                    'rgba(14, 165, 233, 0.7)',  // Abertas (Sky)
                    'rgba(245, 158, 11, 0.7)',  // Em Curso (Amber)
                    'rgba(168, 85, 247, 0.7)',  // Aguard. Peça (Purple)
                    'rgba(16, 185, 129, 0.7)'   // Concluídas (Emerald)
                ],
                borderColor: 'rgba(15, 23, 42, 1)', // slate-900 border
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#e2e8f0' } }
            },
            cutout: '70%'
        }
    });
});