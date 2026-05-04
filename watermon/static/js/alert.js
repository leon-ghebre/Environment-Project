function onSiteChange() { loadAlerts(); }

async function loadAlerts() {
  const days = document.getElementById('al-days').value;
  const url  = `/api/alerts?site=${encodeURIComponent(window.currentSite)}&days=${days}`;
  try {
    const alerts = await apiFetch(url);
    renderSummary(alerts);
    renderList(alerts);
  } catch { showToast('❌ Failed to load alerts'); }
}

function renderSummary(alerts) {
  const total = alerts.length;
  document.getElementById('al-summary').innerHTML = `
    <div class="alert-sum-card">
      <div class="stat-label">Total</div>
      <div class="stat-val">${total}</div>
    </div>
  `;
}

function renderList(alerts) {
  const tbody = document.getElementById('al-list');
  if (!alerts.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="muted">No alerts found.</td></tr>';
    return;
  }
  tbody.innerHTML = alerts.map(a => {
    const m = METRICS[a.metric] || { icon: '⚠️', label: a.metric, unit: '' };
    const sevColor = a.severity === 'high' ? 'var(--critical)' : 'var(--caution)';
    return `
      <tr>
        <td>${a.site}</td>
        <td>${m.icon} ${m.label}</td>
        <td>${fmtDate(a.timestamp)}</td>
        <td style="color:${sevColor}; font-weight:600">${a.severity.toUpperCase()}</td>
      </tr>`;
  }).join('');
}

document.addEventListener('DOMContentLoaded', loadAlerts);
