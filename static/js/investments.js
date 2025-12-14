document.addEventListener('DOMContentLoaded', function() {
  const ctx = document.getElementById('investmentsChart');
  
  // Direkt canvas'tan al
  const pieData = JSON.parse(ctx.dataset.pieChart);
  
  const chartData = {
    labels: [
      'Agriculture, Forestry, Fishing',
      'Environmental Protection',
      'Biodiversity & Landscape',
      'R&D Environmental Protection'
    ],
    datasets: [{
      label: 'Government Expenditure (Million USD)',
      data: [
        pieData.agriculture_forestry_fishing,
        pieData.environmental_protection,
        pieData.biodiversity_landscape,
        pieData.rd_environmental_protection
      ],
      backgroundColor: [
        'rgba(75, 192, 192, 0.8)',
        'rgba(34, 139, 34, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(54, 162, 235, 0.8)'
      ],
      borderColor: [
        'rgba(75, 192, 192, 1)',
        'rgba(34, 139, 34, 1)',
        'rgba(153, 102, 255, 1)',
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
              label += value.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              }) + ' Million USD';
              
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(2);
              label += ' (' + percentage + '%)';
              
              return label;
            }
          }
        }
      }
    }
  };

  new Chart(ctx, config);
});