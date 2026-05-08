// Theme management (handled in external theme.js)
    import { getJSON } from "./api.js";
    // Display current date in page header
    document.getElementById('today-date').textContent = new Date().toLocaleDateString('en-GB', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });

    // Show/hide custom date range inputs
    // eslint-disable-next-line no-unused-vars
    function onDaysChange() {
      const val = document.getElementById('ex-days').value;
      document.getElementById('custom-date-group').style.display = val === 'custom' ? 'flex' : 'none';
      if (val === 'custom') {
        const to = new Date(), from = new Date();
        from.setDate(from.getDate() - 30);
        document.getElementById('ex-to').value   = to.toISOString().slice(0,10);
        document.getElementById('ex-from').value = from.toISOString().slice(0,10);
      }
      updateSummary();
    }

    // Update summary display with current filter selections
    function updateSummary() {
      const site = document.getElementById('ex-site').value || 'All Sites';
      const days = document.getElementById('ex-days').value;
      document.getElementById('sum-site').textContent = site;
      if (days === 'custom') {
        const from = document.getElementById('ex-from').value;
        const to   = document.getElementById('ex-to').value;
        document.getElementById('sum-period').textContent = from && to ? `${from} → ${to}` : 'Custom range';
      } else {
        document.getElementById('sum-period').textContent = `Last ${days} days`;
      }
    }

    // Build query parameters for API requests
    function getParams() {
      const site = document.getElementById('ex-site').value;
      const days = document.getElementById('ex-days').value;
      if (days === 'custom') {
        return `site_code=${encodeURIComponent(site)}&start=${document.getElementById('ex-from').value}&end=${document.getElementById('ex-to').value}`;
      }
      const to = new Date().toISOString().slice(0, 10);
      const from = new Date();
      from.setDate(from.getDate() - parseInt(days));
      return `site_code=${encodeURIComponent(site)}&start=2022-01-01&end=2023-12-31`;
    }

    // Fetch and display preview data from API
    async function refreshPreview() {
      const tbody = document.getElementById('ex-tbody');
      const meta  = document.getElementById('ex-meta');
      tbody.innerHTML = '<tr><td colspan="10" class="muted">Loading…</td></tr>';
      try {
        const rows = await getJSON(`/export?${getParams()}`);
        renderPreview(rows, meta, tbody);
      } catch {
        const demo = Array.from({ length: 8 }, (_, i) => ({
          timestamp:    new Date(Date.now() - i * 3600000).toISOString(),
          site:         ['Upstream','Downstream','Reservoir'][i % 3],
          ph:           (7 + Math.random()).toFixed(2),
          turbidity:    (Math.random() * 10).toFixed(1),
          conductivity: (Math.random() * 500).toFixed(0),
          water_temp:   (15 + Math.random() * 5).toFixed(1),
          water_level:  (Math.random() * 2).toFixed(2),
          air_temp:     (18 + Math.random() * 4).toFixed(1),
          humidity:     (60 + Math.random() * 20).toFixed(0),
          rainfall:     (Math.random() * 5).toFixed(1),
        }));
        renderPreview(demo, meta, tbody);
      }
    }

    // Render data rows in preview table
    function renderPreview(rows, meta, tbody) {
      document.getElementById('sum-rows').textContent = rows.length;
      meta.textContent = `Showing ${rows.length} rows (preview only)`;
      if (!rows.length) { tbody.innerHTML = '<tr><td colspan="10" class="muted">No data.</td></tr>'; return; }
      tbody.innerHTML = rows.map(r => `<tr>
        <td>${fmtDate(r.timestamp)}</td><td>${r.site||'—'}</td>
        <td>${r.ph??'—'}</td><td>${r.turbidity??'—'}</td><td>${r.conductivity??'—'}</td>
        <td>${r.water_temp??'—'}</td><td>${r.water_level??'—'}</td>
        <td>${r.air_temp??'—'}</td><td>${r.humidity??'—'}</td><td>${r.rainfall??'—'}</td>
      </tr>`).join('');
    }

    // Format timestamp to locale string
    function fmtDate(ts) {
      if (!ts) {return '—';}
      return new Date(ts).toLocaleString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    }

    // Download exported data as CSV or JSON file
    // eslint-disable-next-line no-unused-vars
    async function doExport(fmt) {
      try {
        const res  = await fetch(`/export?${getParams()}&format=${fmt}`);
        const blob = await res.blob();
        const a    = document.createElement('a');
        a.href     = URL.createObjectURL(blob);
        const days = document.getElementById('ex-days').value;
        const tag  = days === 'custom'
          ? `${document.getElementById('ex-from').value}_${document.getElementById('ex-to').value}`
          : `${days}d`;
        a.download = `water-data-${tag}.${fmt}`;
        a.click();
      } catch { alert('Export failed — check your connection.'); }
    }
    window.onDaysChange = onDaysChange;
    window.updateSummary = updateSummary;
    window.doExport = doExport;

    // Initialize page: update summary and load preview data
    document.addEventListener('DOMContentLoaded', () => {
      document.getElementById('ex-from').value = '2022-01-01';
      document.getElementById('ex-to').value   = '2023-12-31';
      updateSummary();
    });