/* ==========================================================================
   Chart.js Helper Module for Skill Gap & Performance Visualizations
   ========================================================================== */

let radarChartInstance = null;
let gapBarChartInstance = null;
let gapPieChartInstance = null;

function renderDashboardRadar(gapData) {
  const ctx = document.getElementById('dashboardRadarChart');
  if (!ctx) return;

  const skills = [...(gapData.strong_skills || []), ...(gapData.average_skills || []), ...(gapData.weak_skills || []), ...(gapData.missing_skills || [])];
  if (skills.length === 0) return;

  const labels = skills.map(s => s.skill_name);
  const scores = skills.map(s => s.mastery_score);
  const required = skills.map(s => 80); // Benchmark target line

  if (radarChartInstance) {
    radarChartInstance.destroy();
  }

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#9ca3af' : '#475569';
  const gridColor = isDark ? '#1f2937' : '#e2e8f0';

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Current Mastery Score (%)',
          data: scores,
          backgroundColor: 'rgba(79, 70, 229, 0.25)',
          borderColor: '#4f46e5',
          pointBackgroundColor: '#4f46e5',
          borderWidth: 2
        },
        {
          label: 'Target Career Benchmark',
          data: required,
          backgroundColor: 'rgba(6, 182, 212, 0.1)',
          borderColor: '#06b6d4',
          borderDash: [4, 4],
          pointRadius: 0,
          borderWidth: 1.5
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: gridColor },
          grid: { color: gridColor },
          pointLabels: { color: textColor, font: { family: 'Inter', size: 11, weight: '600' } },
          ticks: { backdropColor: 'transparent', color: textColor, min: 0, max: 100 }
        }
      },
      plugins: {
        legend: { labels: { color: textColor, font: { family: 'Inter' } } }
      }
    }
  });
}

function renderGapPieChart(counts) {
  const ctx = document.getElementById('gapPieChart');
  if (!ctx) return;

  if (gapPieChartInstance) {
    gapPieChartInstance.destroy();
  }

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#9ca3af' : '#475569';

  gapPieChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Strong (>=80%)', 'Average (60-79%)', 'Weak (40-59%)', 'Missing Prereq (<40%)'],
      datasets: [{
        data: [counts.strong || 0, counts.average || 0, counts.weak || 0, counts.missing || 0],
        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#f43f5e'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: textColor, font: { family: 'Inter', size: 11 } } }
      }
    }
  });
}

function renderGapBarChart(gapData) {
  const ctx = document.getElementById('gapBarChart');
  if (!ctx) return;

  const skills = [...(gapData.strong_skills || []), ...(gapData.average_skills || []), ...(gapData.weak_skills || []), ...(gapData.missing_skills || [])];
  if (skills.length === 0) return;

  const labels = skills.map(s => s.skill_name);
  const scores = skills.map(s => s.mastery_score);

  if (gapBarChartInstance) {
    gapBarChartInstance.destroy();
  }

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#9ca3af' : '#475569';
  const gridColor = isDark ? '#1f2937' : '#e2e8f0';

  gapBarChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Mastery Score (%)',
        data: scores,
        backgroundColor: scores.map(s => s >= 80 ? '#10b981' : s >= 60 ? '#3b82f6' : s >= 40 ? '#f59e0b' : '#f43f5e'),
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false }, ticks: { color: textColor, font: { family: 'Inter', size: 10 } } },
        y: { grid: { color: gridColor }, ticks: { color: textColor }, min: 0, max: 100 }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}
