document.addEventListener('DOMContentLoaded', function() {
  const ctx = document.getElementById('landUseChart');
  
  // Direkt canvas'tan al
  const pieData = JSON.parse(ctx.dataset.pieChart);
  
  const chartData = {
    labels: [
      'Arable Land',
      'Permanent Crops',
      'Meadows & Pastures',
      'Forest Land',
      'Other Land',
      'Inland Waters'
    ],
    datasets: [{
      label: 'Land Use (1000 ha)',
      data: [
        pieData.arable_land,
        pieData.permanent_crops,
        pieData.meadows_pastures,
        pieData.forest_land,
        pieData.other_land,
        pieData.inland_waters
      ],
      backgroundColor: [
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(34, 139, 34, 0.8)',
        'rgba(201, 203, 207, 0.8)',
        'rgba(54, 162, 235, 0.8)'
      ],
      borderColor: [
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(34, 139, 34, 1)',
        'rgba(201, 203, 207, 1)',
        'rgba(54, 162, 235, 1)'
      ],
      borderWidth: 2
    }]
  };

  const config = {
    type: 'pie',
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 8,
            font: {
              size: 10
            }
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
              label += value.toLocaleString() + ' (1000 ha)';
              
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(2);
              label += ' - ' + percentage + '%';
              
              return label;
            }
          }
        }
      }
    }
  };

  new Chart(ctx, config);
});