/**
 * SmartExpense Dashboard Visualizations
 * Chart.js configurations for Spending Overview Area Chart & Categories Doughnut Chart
 */

let spendingChart = null;
let categoryChart = null;

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardCharts();

  // Listen for theme change to update chart grid/label colors
  window.addEventListener('themeChanged', () => {
    if (spendingChart || categoryChart) {
      loadDashboardCharts();
    }
  });
});

async function loadDashboardCharts() {
  const urlParams = new URLSearchParams(window.location.search);
  const year = urlParams.get('year') || '';
  const month = urlParams.get('month') || '';

  try {
    const res = await fetch(`/api/dashboard/chart-data?year=${year}&month=${month}`);
    if (!res.ok) return;
    const data = await res.json();

    renderSpendingTrend(data.trend);
    renderCategoryDoughnut(data.categories);
  } catch (err) {
    console.error('Error fetching dashboard chart data:', err);
  }
}

function getChartColors() {
  const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
  return {
    textColor: isDark ? '#94A3B8' : '#64748B',
    gridColor: isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)',
    cardBg: isDark ? '#131D31' : '#FFFFFF'
  };
}

function renderSpendingTrend(trendData, viewMode = 'daily') {
  const ctx = document.getElementById('spendingOverviewChart');
  if (!ctx) return;

  const { textColor, gridColor } = getChartColors();
  const values = viewMode === 'cumulative' ? trendData.cumulative_amounts : trendData.daily_amounts;

  if (spendingChart) {
    spendingChart.destroy();
  }

  // Create gradient fill
  const chartContext = ctx.getContext('2d');
  const gradient = chartContext.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(99, 102, 241, 0.35)');
  gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

  spendingChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: trendData.labels,
      datasets: [{
        label: viewMode === 'cumulative' ? 'Cumulative Spend (₹)' : 'Daily Spend (₹)',
        data: values,
        borderColor: '#6366F1',
        borderWidth: 2.5,
        backgroundColor: gradient,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#6366F1',
        pointHoverRadius: 6,
        pointRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1E293B',
          titleColor: '#F8FAFC',
          bodyColor: '#CBD5E1',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (context) => `₹${context.raw.toLocaleString('en-IN')}`
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
            callback: (val) => `₹${val.toLocaleString('en-IN')}`
          },
          beginAtZero: true
        }
      }
    }
  });
}

function renderCategoryDoughnut(catData) {
  const ctx = document.getElementById('categoryDoughnutChart');
  if (!ctx) return;

  if (categoryChart) {
    categoryChart.destroy();
  }

  if (!catData.amounts.length || catData.amounts.every(v => v === 0)) {
    // Empty state
    return;
  }

  categoryChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: catData.labels,
      datasets: [{
        data: catData.amounts,
        backgroundColor: catData.colors,
        borderWidth: 2,
        borderColor: document.documentElement.getAttribute('data-theme') === 'light' ? '#FFF' : '#131D31'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1E293B',
          padding: 10,
          callbacks: {
            label: (context) => ` ${context.label}: ₹${context.raw.toLocaleString('en-IN')}`
          }
        }
      }
    }
  });
}

function switchTrendView(mode) {
  const dailyBtn = document.getElementById('trendDailyBtn');
  const cumBtn = document.getElementById('trendCumBtn');

  if (mode === 'daily') {
    dailyBtn.classList.add('btn-primary');
    dailyBtn.classList.remove('btn-outline');
    cumBtn.classList.remove('btn-primary');
    cumBtn.classList.add('btn-outline');
  } else {
    cumBtn.classList.add('btn-primary');
    cumBtn.classList.remove('btn-outline');
    dailyBtn.classList.remove('btn-primary');
    dailyBtn.classList.add('btn-outline');
  }

  const urlParams = new URLSearchParams(window.location.search);
  const year = urlParams.get('year') || '';
  const month = urlParams.get('month') || '';

  fetch(`/api/dashboard/chart-data?year=${year}&month=${month}`)
    .then(r => r.json())
    .then(data => renderSpendingTrend(data.trend, mode));
}
