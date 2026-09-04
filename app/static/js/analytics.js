/**
 * SmartExpense Analytics Deep Dive Visualizations
 * Multi-month comparison Chart (Income vs Expense vs Net Savings)
 */

let historyChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadHistoricalChart();

  window.addEventListener('themeChanged', () => {
    if (historyChart) {
      loadHistoricalChart();
    }
  });
});

async function loadHistoricalChart() {
  const ctx = document.getElementById('historicalTrendChart');
  if (!ctx) return;

  try {
    const res = await fetch('/api/analytics/monthly-trend');
    if (!res.ok) return;
    const data = await res.json();

    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const textColor = isDark ? '#94A3B8' : '#64748B';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)';

    if (historyChart) {
      historyChart.destroy();
    }

    historyChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Income',
            data: data.income,
            backgroundColor: '#10B981',
            borderRadius: 6,
            barPercentage: 0.6,
            categoryPercentage: 0.7
          },
          {
            label: 'Expenses',
            data: data.expense,
            backgroundColor: '#F43F5E',
            borderRadius: 6,
            barPercentage: 0.6,
            categoryPercentage: 0.7
          },
          {
            label: 'Net Savings',
            data: data.savings,
            type: 'line',
            borderColor: '#6366F1',
            borderWidth: 3,
            fill: false,
            tension: 0.3,
            pointBackgroundColor: '#6366F1',
            pointRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: textColor,
              boxWidth: 12,
              font: { size: 12, family: 'Plus Jakarta Sans' }
            }
          },
          tooltip: {
            backgroundColor: '#1E293B',
            padding: 10,
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ?${ctx.raw.toLocaleString('en-IN')}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { size: 11 } }
          },
          y: {
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              font: { size: 11 },
              callback: (val) => `?${val.toLocaleString('en-IN')}`
            },
            beginAtZero: true
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading analytics trend chart:', err);
  }
}
