/**
 * test_frontend.js
 *
 * Unit tests for frontend JavaScript functions.
 * Tests pure logic functions that can run without a browser or DOM.
 *
 * Run with: npx jest test_frontend.js
 *
 * Persona coverage:
 *  - Lebo Xhosa: tests for date formatting and summary display logic
 *  - Jack Wilshere: tests for parameter building and export filename generation
 *  - George Weah: tests for alert filtering and severity rendering logic
 */

// ── fmtDate ───────────────────────────────────────────────────────────────────
// Shared by alerts.js and export.js

function fmtDate(ts) {
  if (!ts) { return '—'; }
  return new Date(ts).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

describe('fmtDate', () => {
  test('returns — for null input', () => {
    expect(fmtDate(null)).toBe('—');
  });

  test('returns — for undefined input', () => {
    expect(fmtDate(undefined)).toBe('—');
  });

  test('returns — for empty string', () => {
    expect(fmtDate('')).toBe('—');
  });

  test('returns formatted string for valid ISO timestamp', () => {
    const result = fmtDate('2023-06-15T08:30:00.000Z');
    expect(typeof result).toBe('string');
    expect(result).not.toBe('—');
    expect(result.length).toBeGreaterThan(0);
  });

  test('includes year in output for valid timestamp', () => {
    const result = fmtDate('2023-06-15T08:30:00.000Z');
    expect(result).toContain('2023');
  });
});

// ── Alert filtering logic ────────────────────────────────────────────────────
// From alerts.js — client-side filtering applied after API call

function filterAlerts(alerts, { site, severity, from, to, activeSensors, allSensors }) {
  let filtered = [...alerts];
  if (from)     { filtered = filtered.filter(a => a.timestamp >= from); }
  if (to)       { filtered = filtered.filter(a => a.timestamp.slice(0, 10) <= to); }
  if (site)     { filtered = filtered.filter(a => a.site === site); }
  if (severity) { filtered = filtered.filter(a => a.severity === severity); }
  if (activeSensors && activeSensors.length < allSensors) {
    filtered = filtered.filter(a => activeSensors.includes(a.metric));
  }
  return filtered;
}

const mockAlerts = [
  { site: 'Upstream',   metric: 'ph',        timestamp: '2023-06-15T08:00:00', severity: 'high'   },
  { site: 'Downstream', metric: 'turbidity',  timestamp: '2023-06-16T10:00:00', severity: 'medium' },
  { site: 'Upstream',   metric: 'turbidity',  timestamp: '2023-06-17T12:00:00', severity: 'high'   },
  { site: 'Reservoir',  metric: 'flow',       timestamp: '2023-06-18T14:00:00', severity: 'medium' },
  { site: 'Downstream', metric: 'ph',         timestamp: '2023-06-19T16:00:00', severity: 'high'   },
];

describe('filterAlerts — site filter', () => {
  test('returns only alerts for specified site', () => {
    const result = filterAlerts(mockAlerts, { site: 'Upstream', allSensors: 4 });
    expect(result.every(a => a.site === 'Upstream')).toBe(true);
  });

  test('returns all alerts when no site specified', () => {
    const result = filterAlerts(mockAlerts, { allSensors: 4 });
    expect(result.length).toBe(5);
  });

  test('returns empty array for site with no alerts', () => {
    const result = filterAlerts(mockAlerts, { site: 'NonExistentSite', allSensors: 4 });
    expect(result.length).toBe(0);
  });
});

describe('filterAlerts — severity filter', () => {
  test('returns only high severity alerts', () => {
    const result = filterAlerts(mockAlerts, { severity: 'high', allSensors: 4 });
    expect(result.every(a => a.severity === 'high')).toBe(true);
    expect(result.length).toBe(3);
  });

  test('returns only medium severity alerts', () => {
    const result = filterAlerts(mockAlerts, { severity: 'medium', allSensors: 4 });
    expect(result.every(a => a.severity === 'medium')).toBe(true);
    expect(result.length).toBe(2);
  });
});

describe('filterAlerts — date range filter', () => {
  test('filters out alerts before start date', () => {
    const result = filterAlerts(mockAlerts, { from: '2023-06-17', allSensors: 4 });
    expect(result.every(a => a.timestamp >= '2023-06-17')).toBe(true);
  });

  test('filters out alerts after end date', () => {
    const result = filterAlerts(mockAlerts, { to: '2023-06-16', allSensors: 4 });
    expect(result.every(a => a.timestamp.slice(0, 10) <= '2023-06-16')).toBe(true);
  });

  test('applies both start and end date correctly', () => {
    const result = filterAlerts(mockAlerts, { from: '2023-06-16', to: '2023-06-17', allSensors: 4 });
    expect(result.length).toBe(2);
  });
});

describe('filterAlerts — sensor filter', () => {
  test('filters to only selected sensors', () => {
    const result = filterAlerts(mockAlerts, { activeSensors: ['ph'], allSensors: 4 });
    expect(result.every(a => a.metric === 'ph')).toBe(true);
  });

  test('does not filter when all sensors are active', () => {
    const result = filterAlerts(mockAlerts, { activeSensors: ['ph', 'turbidity', 'flow', 'level'], allSensors: 4 });
    expect(result.length).toBe(5);
  });
});

describe('filterAlerts — combined filters', () => {
  test('applies site and severity together', () => {
    const result = filterAlerts(mockAlerts, { site: 'Upstream', severity: 'high', allSensors: 4 });
    expect(result.every(a => a.site === 'Upstream' && a.severity === 'high')).toBe(true);
    expect(result.length).toBe(2);
  });
});

// ── renderSummary logic ──────────────────────────────────────────────────────

function getSummaryStats(alerts) {
  return {
    total:  alerts.length,
    high:   alerts.filter(a => a.severity === 'high').length,
    medium: alerts.filter(a => a.severity === 'medium').length,
  };
}

describe('getSummaryStats', () => {
  test('returns correct total count', () => {
    expect(getSummaryStats(mockAlerts).total).toBe(5);
  });

  test('returns correct high severity count', () => {
    expect(getSummaryStats(mockAlerts).high).toBe(3);
  });

  test('returns correct medium severity count', () => {
    expect(getSummaryStats(mockAlerts).medium).toBe(2);
  });

  test('returns zeros for empty array', () => {
    const result = getSummaryStats([]);
    expect(result.total).toBe(0);
    expect(result.high).toBe(0);
    expect(result.medium).toBe(0);
  });
});

// ── Export filename generation ────────────────────────────────────────────────
// From export.js — generates download filename based on filters

function buildExportFilename(site, days, from, to, fmt) {
  const tag = days === 'custom'
    ? `${from}_${to}`
    : `${days}d`;
  const siteTag = site ? site.replace(/\s+/g, '-').toLowerCase() : 'all';
  return `water-data-${siteTag}-${tag}.${fmt}`;
}

describe('buildExportFilename', () => {
  test('generates filename with days range', () => {
    const result = buildExportFilename('Upstream', '30', null, null, 'csv');
    expect(result).toBe('water-data-upstream-30d.csv');
  });

  test('generates filename with custom date range', () => {
    const result = buildExportFilename('Downstream', 'custom', '2023-01-01', '2023-06-30', 'csv');
    expect(result).toBe('water-data-downstream-2023-01-01_2023-06-30.csv');
  });

  test('uses all-sites tag when no site selected', () => {
    const result = buildExportFilename('', '7', null, null, 'csv');
    expect(result).toBe('water-data-all-7d.csv');
  });

  test('supports json format', () => {
    const result = buildExportFilename('Upstream', '7', null, null, 'json');
    expect(result).toContain('.json');
  });
});

// ── URL parameter building ────────────────────────────────────────────────────
// From export.js — builds query string for API requests

function buildQueryParams(site, days, from, to) {
  if (days === 'custom') {
    return `site=${encodeURIComponent(site)}&from=${from}&to=${to}`;
  }
  return `site=${encodeURIComponent(site)}&days=${days}`;
}

describe('buildQueryParams', () => {
  test('builds params with days range', () => {
    const result = buildQueryParams('Upstream', '30', null, null);
    expect(result).toBe('site=Upstream&days=30');
  });

  test('builds params with custom date range', () => {
    const result = buildQueryParams('Downstream', 'custom', '2023-01-01', '2023-06-30');
    expect(result).toBe('site=Downstream&from=2023-01-01&to=2023-06-30');
  });

  test('URL encodes site name with spaces', () => {
    const result = buildQueryParams('Site Upstream', '7', null, null);
    expect(result).toContain('Site%20Upstream');
  });

  test('handles empty site', () => {
    const result = buildQueryParams('', '7', null, null);
    expect(result).toContain('site=');
  });
});

// ── loadLiveData data extraction logic ───────────────────────────────────────
// From index.js — extracts latest values from timeseries response

function extractLatestValues(phData, turbidityData, levelData, temperatureData) {
  return {
    recorded_at:       phData[phData.length - 1].recorded_at,
    ph:                phData[phData.length - 1].avg,
    turbidity_ntu:     turbidityData[turbidityData.length - 1].avg,
    water_level_cm:    levelData[levelData.length - 1].avg,
    water_temperature_c: temperatureData[temperatureData.length - 1].avg,
  };
}

const mockTimeseries = {
  ph:          [{ recorded_at: '2023-01-01', avg: 7.1 }, { recorded_at: '2023-01-02', avg: 7.3 }],
  turbidity:   [{ recorded_at: '2023-01-01', avg: 2.5 }, { recorded_at: '2023-01-02', avg: 3.1 }],
  level:       [{ recorded_at: '2023-01-01', avg: 120 }, { recorded_at: '2023-01-02', avg: 125 }],
  temperature: [{ recorded_at: '2023-01-01', avg: 18.5 }, { recorded_at: '2023-01-02', avg: 19.0 }],
};

describe('extractLatestValues', () => {
  test('returns the most recent ph value', () => {
    const result = extractLatestValues(mockTimeseries.ph, mockTimeseries.turbidity, mockTimeseries.level, mockTimeseries.temperature);
    expect(result.ph).toBe(7.3);
  });

  test('returns the most recent turbidity value', () => {
    const result = extractLatestValues(mockTimeseries.ph, mockTimeseries.turbidity, mockTimeseries.level, mockTimeseries.temperature);
    expect(result.turbidity_ntu).toBe(3.1);
  });

  test('returns the most recent recorded_at timestamp', () => {
    const result = extractLatestValues(mockTimeseries.ph, mockTimeseries.turbidity, mockTimeseries.level, mockTimeseries.temperature);
    expect(result.recorded_at).toBe('2023-01-02');
  });

  test('returns the most recent water level', () => {
    const result = extractLatestValues(mockTimeseries.ph, mockTimeseries.turbidity, mockTimeseries.level, mockTimeseries.temperature);
    expect(result.water_level_cm).toBe(125);
  });

  test('returns the most recent temperature', () => {
    const result = extractLatestValues(mockTimeseries.ph, mockTimeseries.turbidity, mockTimeseries.level, mockTimeseries.temperature);
    expect(result.water_temperature_c).toBe(19.0);
  });
});

// ── hasData check ─────────────────────────────────────────────────────────────
// From advanced-graphs.js — determines whether any sensor returned data

function hasAnyData(results) {
  return results.some(({ data }) => data.length > 0);
}

describe('hasAnyData', () => {
  test('returns true when at least one sensor has data', () => {
    const results = [{ id: 'ph', data: [{ recorded_at: '2023-01-01', avg: 7.2 }] }, { id: 'turbidity', data: [] }];
    expect(hasAnyData(results)).toBe(true);
  });

  test('returns false when all sensors return empty data', () => {
    const results = [{ id: 'ph', data: [] }, { id: 'turbidity', data: [] }];
    expect(hasAnyData(results)).toBe(false);
  });

  test('returns false for empty results array', () => {
    expect(hasAnyData([])).toBe(false);
  });

  test('returns true when all sensors have data', () => {
    const results = [
      { id: 'ph',        data: [{ recorded_at: '2023-01-01', avg: 7.2 }] },
      { id: 'turbidity', data: [{ recorded_at: '2023-01-01', avg: 3.1 }] },
    ];
    expect(hasAnyData(results)).toBe(true);
  });
});
