document.addEventListener('DOMContentLoaded', function() {

  // Chart 1: Exports vs Imports Over Time (Line Chart)
  const exportsImportsCtx = document.getElementById('exportsImportsChart');
  if (exportsImportsCtx && exportsImportsCtx.dataset.chart) {
    const timeSeriesData = JSON.parse(exportsImportsCtx.dataset.chart);

    new Chart(exportsImportsCtx, {
      type: 'line',
      data: {
        labels: timeSeriesData.labels,
        datasets: [
          {
            label: 'Exports',
            data: timeSeriesData.exports,
            borderColor: 'rgba(39, 174, 96, 1)',
            backgroundColor: 'rgba(39, 174, 96, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          },
          {
            label: 'Imports',
            data: timeSeriesData.imports,
            borderColor: 'rgba(52, 152, 219, 1)',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              font: { size: 12 }
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                label += '$' + context.parsed.y.toLocaleString();
                return label;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + (value / 1000000).toFixed(0) + 'M';
              }
            }
          }
        }
      }
    });
  }

  // Chart 2: Top Trading Countries (Horizontal Bar Chart)
  const topCountriesCtx = document.getElementById('topCountriesChart');
  if (topCountriesCtx && topCountriesCtx.dataset.chart) {
    const topCountriesData = JSON.parse(topCountriesCtx.dataset.chart);

    new Chart(topCountriesCtx, {
      type: 'bar',
      data: {
        labels: topCountriesData.labels,
        datasets: [{
          label: 'Total Trade Value',
          data: topCountriesData.values,
          backgroundColor: 'rgba(52, 152, 219, 0.8)',
          borderColor: 'rgba(52, 152, 219, 1)',
          borderWidth: 1
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return '$' + context.parsed.x.toLocaleString();
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + (value / 1000000).toFixed(0) + 'M';
              }
            }
          }
        }
      }
    });
  }

  // Chart 3: Trade Balance by Country (Bar Chart with Positive/Negative)
  const tradeBalanceCtx = document.getElementById('tradeBalanceChart');
  if (tradeBalanceCtx && tradeBalanceCtx.dataset.chart) {
    const tradeBalanceData = JSON.parse(tradeBalanceCtx.dataset.chart);

    // Color bars based on positive (surplus) or negative (deficit)
    const backgroundColors = tradeBalanceData.balance.map(val =>
      val >= 0 ? 'rgba(39, 174, 96, 0.8)' : 'rgba(231, 76, 60, 0.8)'
    );
    const borderColors = tradeBalanceData.balance.map(val =>
      val >= 0 ? 'rgba(39, 174, 96, 1)' : 'rgba(231, 76, 60, 1)'
    );

    new Chart(tradeBalanceCtx, {
      type: 'bar',
      data: {
        labels: tradeBalanceData.labels,
        datasets: [{
          label: 'Trade Balance',
          data: tradeBalanceData.balance,
          backgroundColor: backgroundColors,
          borderColor: borderColors,
          borderWidth: 1
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const value = context.parsed.x;
                const prefix = value >= 0 ? 'Surplus: $' : 'Deficit: $';
                return prefix + Math.abs(value).toLocaleString();
              }
            }
          }
        },
        scales: {
          x: {
            ticks: {
              callback: function(value) {
                return '$' + (value / 1000000).toFixed(0) + 'M';
              }
            }
          }
        }
      }
    });
  }

  // Chart 4: Top Commodities Traded (Doughnut Chart)
  const commoditiesCtx = document.getElementById('commoditiesChart');
  if (commoditiesCtx && commoditiesCtx.dataset.chart) {
    const commoditiesData = JSON.parse(commoditiesCtx.dataset.chart);

    new Chart(commoditiesCtx, {
      type: 'doughnut',
      data: {
        labels: commoditiesData.labels,
        datasets: [{
          label: 'Trade Value',
          data: commoditiesData.values,
          backgroundColor: [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(46, 204, 113, 0.8)',
            'rgba(231, 76, 60, 0.8)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(46, 204, 113, 1)',
            'rgba(231, 76, 60, 1)'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 10,
              font: { size: 10 }
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.label || '';
                if (label) {
                  label += ': ';
                }
                const value = context.parsed;
                label += '$' + value.toLocaleString();

                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                label += ' (' + percentage + '%)';

                return label;
              }
            }
          }
        }
      }
    });
  }

  // Chart 5: Regional Trade Distribution (Pie Chart)
  const regionalCtx = document.getElementById('regionalChart');
  if (regionalCtx && regionalCtx.dataset.chart) {
    const regionalData = JSON.parse(regionalCtx.dataset.chart);

    new Chart(regionalCtx, {
      type: 'pie',
      data: {
        labels: regionalData.labels,
        datasets: [{
          label: 'Trade Value',
          data: regionalData.values,
          backgroundColor: [
            'rgba(52, 152, 219, 0.8)',
            'rgba(46, 204, 113, 0.8)',
            'rgba(155, 89, 182, 0.8)',
            'rgba(241, 196, 15, 0.8)',
            'rgba(231, 76, 60, 0.8)',
            'rgba(26, 188, 156, 0.8)',
            'rgba(230, 126, 34, 0.8)'
          ],
          borderColor: [
            'rgba(52, 152, 219, 1)',
            'rgba(46, 204, 113, 1)',
            'rgba(155, 89, 182, 1)',
            'rgba(241, 196, 15, 1)',
            'rgba(231, 76, 60, 1)',
            'rgba(26, 188, 156, 1)',
            'rgba(230, 126, 34, 1)'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 10,
              font: { size: 10 }
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.label || '';
                if (label) {
                  label += ': ';
                }
                const value = context.parsed;
                label += '$' + value.toLocaleString();

                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                label += ' (' + percentage + '%)';

                return label;
              }
            }
          }
        }
      }
    });
  }

  // Chart 6: Trade Volume Over Time (Area Chart)
  const volumeCtx = document.getElementById('volumeChart');
  if (volumeCtx && volumeCtx.dataset.chart) {
    const volumeData = JSON.parse(volumeCtx.dataset.chart);

    new Chart(volumeCtx, {
      type: 'line',
      data: {
        labels: volumeData.labels,
        datasets: [{
          label: 'Total Trade Value',
          data: volumeData.values,
          borderColor: 'rgba(155, 89, 182, 1)',
          backgroundColor: 'rgba(155, 89, 182, 0.3)',
          borderWidth: 2,
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              font: { size: 12 }
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                label += '$' + context.parsed.y.toLocaleString();
                return label;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + (value / 1000000).toFixed(0) + 'M';
              }
            }
          }
        }
      }
    });
  }
});
