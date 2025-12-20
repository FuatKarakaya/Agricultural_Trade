// Timeline Chart
const ctx = document.getElementById('timelineChart');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: chartData.years,
        datasets: [
            {
                label: 'Arable Land',
                data: chartData.arable_land,
                borderColor: '#FF6384',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4
            },
            {
                label: 'Permanent Crops',
                data: chartData.permanent_crops,
                borderColor: '#36A2EB',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4
            },
            {
                label: 'Meadows & Pastures',
                data: chartData.meadows_pastures,
                borderColor: '#FFCE56',
                backgroundColor: 'rgba(255, 206, 86, 0.1)',
                tension: 0.4
            },
            {
                label: 'Forest Land',
                data: chartData.forest_land,
                borderColor: '#4BC0C0',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4
            },
            {
                label: 'Other Land',
                data: chartData.other_land,
                borderColor: '#9966FF',
                backgroundColor: 'rgba(153, 102, 255, 0.1)',
                tension: 0.4
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += new Intl.NumberFormat('en-US').format(context.parsed.y) + ' (1000 ha)';
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Area (1000 ha)'
                },
                ticks: {
                    callback: function(value) {
                        return new Intl.NumberFormat('en-US').format(value);
                    }
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Year'
                }
            }
        }
    }
});