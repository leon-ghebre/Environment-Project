// API endpoint for backend alerts
import { getJSON } from "./api.js";

document.getElementById('today-date').textContent = new Date().toLocaleDateString('en-GB', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
});

// Default date range to match available data
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('dateFrom').value = '2022-01-01';
  document.getElementById('dateTo').value   = '2023-12-31';
});

// Sensor types with labels and colors
const SENSORS = {
  ph:           { label: 'pH',          color: 'var(--color-ph)'        },
  turbidity:    { label: 'Turbidity',   color: 'var(--color-turbidity)' },
  conductivity: { label: 'Conductivity',color: 'var(--color-flow)'      },
  sensor_fault: { label: 'Sensor Fault',color: 'var(--color-level)'     },
};

// Get currently checked sensor filters
function getActiveSensors() {
  return Array.from(document.querySelectorAll('.sensor-checkbox input:checked')).map(cb => cb.value);
}

// Format timestamp to locale string
function fmtDate(ts) {
  if (!ts) { return '—'; }
  return new Date(ts).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  });
}

// Update summary statistics display
function renderSummary(alerts) {
  document.getElementById('al-total').textContent  = alerts.length;
  document.getElementById('al-high').textContent   = alerts.filter(a => a.severity === 'critical').length;
  document.getElementById('al-medium').textContent = alerts.filter(a => a.severity === 'warning').length;
  const from = document.getElementById('dateFrom').value;
  const to   = document.getElementById('dateTo').value;
  document.getElementById('al-period').textContent = `${from} → ${to}`;
}

// Render alert rows in table
function renderList(alerts) {
  const tbody = document.getElementById('al-list');
  if (!alerts.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="muted">No alerts match the current filters.</td></tr>';
    return;
  }
  tbody.innerHTML = alerts.map(a => {
    const s   = SENSORS[a.alert_type] || { label: a.alert_type, color: 'var(--text-3)' };
    const cls = a.severity === 'critical' ? 'sev-high' : 'sev-medium';
    return `<tr>
      <td>${a.site_code || '—'}</td>
      <td><span class="sensor-cell">
        <span style="width:8px;height:8px;border-radius:50%;background:${s.color};display:inline-block;flex-shrink:0"></span>
        ${s.label}
      </span></td>
      <td>${fmtDate(a.timestamp)}</td>
      <td class="${cls}">${(a.severity || '').toUpperCase()}</td>
    </tr>`;
  }).join('');
}

// Fetch alerts from API and apply client-side filters
async function loadAlerts() {
  const site     = document.getElementById('siteSelector').value;
  const severity = document.getElementById('severityFilter').value;
  const from     = document.getElementById('dateFrom').value;
  const to       = document.getElementById('dateTo').value;
  const active   = getActiveSensors();

  let alerts = [];
  try {
    const params = new URLSearchParams();
    if (site)     { params.set('site_code', site); }
    if (from)     { params.set('start', from); }
    if (to)       { params.set('end', to); }
    alerts = await getJSON(`/alerts?${params}`);
  } catch {
    alerts = [];
  }

  // Apply client-side filtering
  if (from)     { alerts = alerts.filter(a => a.timestamp >= from); }
  if (to)       { alerts = alerts.filter(a => a.timestamp.slice(0, 10) <= to); }
  if (site)     { alerts = alerts.filter(a => a.site_code === site); }
  if (severity) { alerts = alerts.filter(a => a.severity === severity); }
  if (active.length < Object.keys(SENSORS).length) {
    alerts = alerts.filter(a => active.includes(a.alert_type));
  }

  renderSummary(alerts);
  renderList(alerts);
}

// Expose to global scope for HTML onclick handlers
window.loadAlerts = loadAlerts;

document.addEventListener('DOMContentLoaded', loadAlerts);