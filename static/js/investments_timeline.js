// Yüzde hesaplamaları
const agriculturePct = chartData.years.map((year, index) => {
    const total = chartData.total_expenditure[index];
    return total > 0 ? (chartData.agriculture_forestry_fishing[index] / total * 100) : 0;
});

const environmentalPct = chartData.years.map((year, index) => {
    const total = chartData.total_expenditure[index];
    return total > 0 ? (chartData.environmental_protection[index] / total * 100) : 0;
});

const biodiversityPct = chartData.years.map((year, index) => {
    const total = chartData.total_expenditure[index];
    return total > 0 ? (chartData.biodiversity_landscape[index] / total * 100) : 0;
});

const rdPct = chartData.years.map((year, index) => {
    const total = chartData.total_expenditure[index];
    return total > 0 ? (chartData.rd_environmental_protection[index] / total * 100) : 0;
});

// Chart 1: Total Expenditure
const ctxTotal = document.getElementById('totalExpenditureChart');
new Chart(ctxTotal, {
    type: 'line',
    data: {
        labels: chartData.years,
        datasets: [
            {
                label: 'Total Expenditure',
                data: chartData.total_expenditure,
                borderColor: '#FF6384',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4,
                borderWidth: 3,
                fill: true
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
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return 'Total: ' + new Intl.NumberFormat('en-US', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        }).format(context.parsed.y) + ' Million USD';
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Total Expenditure (Million USD)'
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

// Chart 2: Percentages (0-10%)
const ctxPercent = document.getElementById('percentageChart');
new Chart(ctxPercent, {
    type: 'line',
    data: {
        labels: chartData.years,
        datasets: [
            {
                label: 'Agriculture, Forestry, Fishing',
                data: agriculturePct,
                borderColor: '#36A2EB',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4,
                borderWidth: 2,
                fill: false
            },
            {
                label: 'Environmental Protection',
                data: environmentalPct,
                borderColor: '#4BC0C0',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4,
                borderWidth: 2,
                fill: false
            },
            {
                label: 'Biodiversity & Landscape',
                data: biodiversityPct,
                borderColor: '#FFCE56',
                backgroundColor: 'rgba(255, 206, 86, 0.1)',
                tension: 0.4,
                borderWidth: 2,
                fill: false
            },
            {
                label: 'R&D Environmental Protection',
                data: rdPct,
                borderColor: '#9966FF',
                backgroundColor: 'rgba(153, 102, 255, 0.1)',
                tension: 0.4,
                borderWidth: 2,
                fill: false
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
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        label += context.parsed.y.toFixed(3) + '%';
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 10,
                title: {
                    display: true,
                    text: 'Percentage of Total Expenditure (%)'
                },
                ticks: {
                    callback: function(value) {
                        return value.toFixed(1) + '%';
                    },
                    stepSize: 0.1
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