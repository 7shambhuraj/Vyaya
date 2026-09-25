

const PALETTE = [
  '#4f8ef7','#ff6b6b','#36d399','#a78bfa',
  '#fb923c','#2dd4bf','#f59e0b','#ec4899',
  '#6366f1','#06b6d4'
];


function initCharts(trendLabels, trendData, catLabels, catData) {                                                                         /* Chart initialisation  */

  Chart.defaults.color = '#8b92b8';
  Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';
  Chart.defaults.font.family = 'DM Sans, sans-serif';

  
  const trendCtx = document.getElementById('trendChart');                                                                           //  Trend bar chart
  if (trendCtx) {
    new Chart(trendCtx, {
      type: 'bar',
      data: {
        labels: trendLabels.length ? trendLabels : ['No data'],
        datasets: [{
          label: 'Expenses (₹)',
          data: trendData.length ? trendData : [0],
          backgroundColor: ctx => {
            const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(79,142,247,.8)');
            gradient.addColorStop(1, 'rgba(79,142,247,.1)');
            return gradient;
          },
          borderColor: '#4f8ef7',
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(19,23,43,.95)',
            borderColor: 'rgba(79,142,247,.3)',
            borderWidth: 1,
            titleFont: { family: 'Syne, sans-serif', weight: '700' },
            callbacks: {
              label: ctx => ` ₹${ctx.parsed.y.toLocaleString('en-IN')}`
            }
          }
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: {
              callback: val => '₹' + (val >= 1000 ? (val/1000).toFixed(0)+'k' : val)
            }
          }
        }
      }
    });
  }

  
  const catCtx = document.getElementById('categoryChart');                                                                          //  Category doughnut
  if (catCtx) {
    const chart = new Chart(catCtx, {
      type: 'doughnut',
      data: {
        labels: catLabels.length ? catLabels : ['No data'],
        datasets: [{
          data: catData.length ? catData : [1],
          backgroundColor: PALETTE,
          borderColor: 'rgba(19,23,43,1)',
          borderWidth: 3,
          hoverOffset: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(19,23,43,.95)',
            borderColor: 'rgba(255,255,255,.07)',
            borderWidth: 1,
            callbacks: {
              label: ctx => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct   = total ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                return ` ₹${ctx.parsed.toLocaleString('en-IN')} (${pct}%)`;
              }
            }
          }
        }
      }
    });

   
    buildLegend(catLabels, catData, PALETTE);
  }
}

function buildLegend(labels, data, colors) {
  const container = document.getElementById('legendList');
  if (!container || !labels.length) return;

  const total = data.reduce((a, b) => a + b, 0);
  container.innerHTML = labels.map((label, i) => {
    const pct = total ? ((data[i] / total) * 100).toFixed(0) : 0;
    return `
      <div class="legend-item">
        <div class="legend-dot" style="background:${colors[i % colors.length]}"></div>
        <span>${label}</span>
        <span>${pct}%</span>
      </div>
    `;
  }).join('');
}


function filterTable() {
  const query = document.getElementById('searchInput').value.toLowerCase();                                                            /*  Table search/filter  */
  document.querySelectorAll('#expenseTable tbody tr').forEach(row => {
    if (row.querySelector('.empty-row')) return;
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(query) ? '' : 'none';
  });
}


function animateCounters() {                                                                                                /* ── Number counter animation for stat cards ────────────────── */
  document.querySelectorAll('.stat-info h3').forEach(el => {
    const raw   = el.textContent.replace(/[₹,]/g, '').trim();
    const num   = parseFloat(raw);
    if (isNaN(num)) return;

    const isRupee = el.textContent.includes('₹');
    const duration = 1000;
    const steps    = 40;
    const inc      = num / steps;
    let current    = 0;
    let step       = 0;

    const timer = setInterval(() => {
      step++;
      current += inc;
      if (step >= steps) { current = num; clearInterval(timer); }
      el.textContent = isRupee
        ? '₹' + Math.round(current).toLocaleString('en-IN')
        : Math.round(current).toLocaleString('en-IN');
    }, duration / steps);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  setTimeout(animateCounters, 200);
});
