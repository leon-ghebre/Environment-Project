"""
Water Monitoring Dashboard — Flask + SQLite backend
"""
from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, json, csv, io, os, random
from datetime import datetime, timedelta

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'water.db')

SITES = ['Upstream', 'Downstream', 'Reservoir']

THRESHOLDS = {
    'ph':           {'min': 6.5,  'max': 8.5,    'unit': '',      'label': 'pH'},
    'turbidity':    {'min': None, 'max': 4.0,    'unit': 'NTU',   'label': 'Turbidity'},
    'conductivity': {'min': None, 'max': 1500.0, 'unit': 'μS/cm', 'label': 'Conductivity'},
    'water_temp':   {'min': 0.0,  'max': 30.0,   'unit': '°C',    'label': 'Water Temp'},
    'water_level':  {'min': None, 'max': 3.5,    'unit': 'm',     'label': 'Water Level'},
    'light':        {'min': None, 'max': 100000, 'unit': 'lux',   'label': 'Light'},
    'air_temp':     {'min': None, 'max': 45.0,   'unit': '°C',    'label': 'Air Temp'},
    'humidity':     {'min': None, 'max': 100.0,  'unit': '%',     'label': 'Humidity'},
    'rainfall':     {'min': None, 'max': 50.0,   'unit': 'mm/h',  'label': 'Rainfall'},
}

# ── Database ──────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL, site TEXT NOT NULL,
            ph REAL, turbidity REAL, conductivity REAL, water_temp REAL,
            water_level REAL, light REAL, air_temp REAL, humidity REAL,
            rainfall REAL, sensor_fault INTEGER DEFAULT 0, notes TEXT
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL, site TEXT NOT NULL,
            metric TEXT NOT NULL, value REAL NOT NULL,
            threshold REAL NOT NULL, direction TEXT NOT NULL,
            severity TEXT NOT NULL, acknowledged INTEGER DEFAULT 0
        )''')
        conn.commit()
        if conn.execute('SELECT COUNT(*) FROM readings').fetchone()[0] == 0:
            _seed(conn)

def _seed(conn):
    now = datetime.now()
    rows = []
    for days_ago in range(30, -1, -1):
        for hour in [0, 6, 12, 18]:
            ts = now - timedelta(days=days_ago, hours=abs(now.hour - hour))
            for site in SITES:
                base_ph   = {'Upstream': 7.2, 'Downstream': 7.0, 'Reservoir': 7.5}[site]
                base_turb = {'Upstream': 1.5, 'Downstream': 2.8, 'Reservoir': 0.8}[site]
                fault = 1 if random.random() < 0.02 else 0
                rows.append((
                    ts.isoformat(), site,
                    round(max(5.0, min(10.0, random.gauss(base_ph, 0.3))), 2),
                    round(max(0.1, random.gauss(base_turb, 0.8)), 2),
                    round(random.gauss(450, 80), 1),
                    round(random.gauss(16, 2), 1),
                    round(max(0.1, random.gauss(1.8, 0.4)), 2),
                    round(max(0, random.gauss(8000, 3000)), 0),
                    round(random.gauss(18, 4), 1),
                    round(max(0, min(100, random.gauss(65, 12))), 1),
                    round(max(0, random.gauss(1, 3)), 1),
                    fault, ''
                ))
    conn.executemany('''INSERT INTO readings
        (timestamp,site,ph,turbidity,conductivity,water_temp,water_level,
         light,air_temp,humidity,rainfall,sensor_fault,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', rows)
    conn.commit()

def row_to_dict(row): return dict(row)

def check_alerts(conn, data, site, timestamp):
    sev_map = {'ph':'high','turbidity':'high','conductivity':'medium',
               'water_temp':'medium','water_level':'high','rainfall':'medium'}
    for metric, lim in THRESHOLDS.items():
        val = data.get(metric)
        if val is None: continue
        val = float(val)
        sev = sev_map.get(metric, 'low')
        if lim['max'] is not None and val > lim['max']:
            conn.execute('INSERT INTO alerts (timestamp,site,metric,value,threshold,direction,severity) VALUES (?,?,?,?,?,?,?)',
                         (timestamp,site,metric,val,lim['max'],'above',sev))
        elif lim['min'] is not None and val < lim['min']:
            conn.execute('INSERT INTO alerts (timestamp,site,metric,value,threshold,direction,severity) VALUES (?,?,?,?,?,?,?)',
                         (timestamp,site,metric,val,lim['min'],'below',sev))

def compute_status(latest):
    if not latest: return 'safe', 'No data available'
    if latest.get('sensor_fault'): return 'caution', 'Sensor fault detected — check equipment'
    issues = []
    for m, lim in THRESHOLDS.items():
        v = latest.get(m)
        if v is None: continue
        if lim['max'] and v > lim['max']: issues.append(m)
        elif lim['min'] and v < lim['min']: issues.append(m)
    if not issues: return 'safe', 'All parameters within safe range'
    critical = [m for m in issues if m in ('ph','turbidity','water_level')]
    if critical: return 'critical', f"Critical: {THRESHOLDS[critical[0]]['label']} out of range"
    return 'caution', f"Caution: {len(issues)} parameter(s) need attention"

# ── Page routes ───────────────────────────────────────────────────────────────
@app.route('/')
def dashboard(): return render_template('dashboard.html')

@app.route('/trends.html')
def trends(): return render_template('trends.html')

@app.route('/alerts.html')
def alerts_page(): return render_template('alerts.html')

@app.route('/export.html')
def export_page(): return render_template('export.html')

# ── API routes ────────────────────────────────────────────────────────────────
@app.route('/api/sites')
def api_sites(): return jsonify(SITES)

@app.route('/api/thresholds')
def api_thresholds(): return jsonify(THRESHOLDS)

@app.route('/api/status')
def api_status():
    site = request.args.get('site', 'Upstream')
    with get_db() as conn:
        row = conn.execute('SELECT * FROM readings WHERE site=? ORDER BY timestamp DESC LIMIT 1',(site,)).fetchone()
    latest = row_to_dict(row) if row else {}
    status, message = compute_status(latest)
    return jsonify({'status': status, 'message': message, 'latest': latest})

@app.route('/api/readings')
def api_readings():
    site  = request.args.get('site', 'Upstream')
    days  = int(request.args.get('days', 7))
    limit = int(request.args.get('limit', 400))
    since = (datetime.now() - timedelta(days=days)).isoformat()
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM readings WHERE site=? AND timestamp>=? ORDER BY timestamp DESC LIMIT ?',
            (site, since, limit)).fetchall()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/api/readings', methods=['POST'])
def api_add_reading():
    data = request.json
    ts   = data.get('timestamp') or datetime.now().isoformat()
    site = data.get('site', 'Upstream')
    with get_db() as conn:
        cur = conn.execute('''INSERT INTO readings
            (timestamp,site,ph,turbidity,conductivity,water_temp,water_level,
             light,air_temp,humidity,rainfall,sensor_fault,notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (ts,site,data.get('ph'),data.get('turbidity'),data.get('conductivity'),
             data.get('water_temp'),data.get('water_level'),data.get('light'),
             data.get('air_temp'),data.get('humidity'),data.get('rainfall'),
             1 if data.get('sensor_fault') else 0, data.get('notes','')))
        check_alerts(conn, data, site, ts)
        conn.commit()
    return jsonify({'success': True, 'id': cur.lastrowid}), 201

@app.route('/api/alerts')
def api_alerts():
    site  = request.args.get('site', '')
    ack   = request.args.get('acknowledged', 'all')
    days  = int(request.args.get('days', 7))
    since = (datetime.now() - timedelta(days=days)).isoformat()
    q, p  = 'SELECT * FROM alerts WHERE timestamp>=?', [since]
    if site:        q += ' AND site=?';           p.append(site)
    if ack=='false': q += ' AND acknowledged=0'
    elif ack=='true':q += ' AND acknowledged=1'
    q += ' ORDER BY timestamp DESC'
    with get_db() as conn:
        rows = conn.execute(q, p).fetchall()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/api/alerts/<int:aid>/acknowledge', methods=['POST'])
def api_ack(aid):
    with get_db() as conn:
        conn.execute('UPDATE alerts SET acknowledged=1 WHERE id=?',(aid,)); conn.commit()
    return jsonify({'success': True})

@app.route('/api/alerts/acknowledge-all', methods=['POST'])
def api_ack_all():
    site = request.args.get('site','')
    with get_db() as conn:
        if site: conn.execute('UPDATE alerts SET acknowledged=1 WHERE site=? AND acknowledged=0',(site,))
        else:    conn.execute('UPDATE alerts SET acknowledged=1 WHERE acknowledged=0')
        conn.commit()
    return jsonify({'success': True})

@app.route('/api/export/csv')
def api_export_csv():
    site  = request.args.get('site','')
    days  = int(request.args.get('days', 30))
    since = (datetime.now()-timedelta(days=days)).isoformat()
    q,p   = 'SELECT * FROM readings WHERE timestamp>=?',[since]
    if site: q+=' AND site=?'; p.append(site)
    with get_db() as conn:
        rows = conn.execute(q+' ORDER BY timestamp',p).fetchall()
    out = io.StringIO()
    w   = csv.writer(out)
    w.writerow(['ID','Timestamp','Site','pH','Turbidity(NTU)','Conductivity(μS/cm)',
                'WaterTemp(°C)','WaterLevel(m)','Light(lux)','AirTemp(°C)',
                'Humidity(%)','Rainfall(mm/h)','SensorFault','Notes'])
    for r in rows:
        w.writerow([r['id'],r['timestamp'],r['site'],r['ph'],r['turbidity'],
                    r['conductivity'],r['water_temp'],r['water_level'],r['light'],
                    r['air_temp'],r['humidity'],r['rainfall'],r['sensor_fault'],r['notes']])
    out.seek(0)
    return send_file(io.BytesIO(out.getvalue().encode()), mimetype='text/csv',
                     as_attachment=True,
                     download_name=f'water_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

@app.route('/api/export/json')
def api_export_json():
    site  = request.args.get('site','')
    days  = int(request.args.get('days', 30))
    since = (datetime.now()-timedelta(days=days)).isoformat()
    q,p   = 'SELECT * FROM readings WHERE timestamp>=?',[since]
    if site: q+=' AND site=?'; p.append(site)
    with get_db() as conn:
        rows = conn.execute(q+' ORDER BY timestamp',p).fetchall()
    data = json.dumps([row_to_dict(r) for r in rows], indent=2)
    return send_file(io.BytesIO(data.encode()), mimetype='application/json',
                     as_attachment=True,
                     download_name=f'water_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

if __name__ == '__main__':
    init_db()
    print('✅  Water Monitoring Dashboard → http://localhost:5000')
    app.run(debug=True, port=5000)
