# Environment Project

Water quality monitoring system designed for environmental researchers, farmers, and public health officers.

The system provides monitoring dashboards, alerts, historical trend analysis, CSV exports, and simulated live sensor streaming.

---

# Features

- Water quality monitoring across multiple sites
- Real-time style streaming simulation
- Alerts and contamination monitoring
- Historical trend analysis
- CSV dataset export
- Sensor fault detection and validation
- Accessibility and high-contrast support
- REST API backend using Flask + SQLAlchemy

---

# Tech Stack

## Backend
- Python
- Flask
- SQLAlchemy
- SQLite
- Pandas

## Frontend
- HTML
- CSS
- JavaScript

## Testing & Tooling
- pytest
- flake8
- black
- pre-commit
- GitHub Actions

---

# Project Structure

```text
backend/
├── app.py
├── scripts/
│   ├── import_water.py
│   └── simulate_stream.py
├── database/
├── routes/
├── services/
├── validation/
├── templates/
├── static/
└── tests/
```

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/leon-ghebre/Environment-Project.git
cd Environment-Project
```

## 2. Install dependencies

```bash
pip install -r backend/requirements.txt
```

---

# Running the Project

The project requires two terminals.

---

## Terminal 1 — Run the Flask Backend

```bash
cd backend
python app.py
```

This starts the Flask API server.

The backend will usually run on:

```text
http://127.0.0.1:5000
```

---

## Terminal 2 — Run the Streaming Simulation

Open a second terminal:

```bash
cd backend
python -m scripts.simulate_stream
```

This simulates live sensor readings being streamed into the database in batches.

The script:

- imports rows in batches
- waits between batches
- simulates live environmental monitoring updates

---

# Example API Endpoints

## Get monitoring sites

```text
GET /sites
```

Example:

```bash
curl "http://127.0.0.1:5000/sites"
```

---

## Get latest reading

```text
GET /latest?site_code=site_upstream
```

Example:

```bash
curl "http://127.0.0.1:5000/latest?site_code=site_upstream"
```

---

## Get alerts

```text
GET /alerts
```

Example:

```bash
curl "http://127.0.0.1:5000/alerts"
```

---

## Get historical timeseries data

```text
GET /timeseries
```

Example:

```bash
curl "http://127.0.0.1:5000/timeseries?site_code=site_upstream&metric=ph&freq=D"
```

---

# Running Tests

## Backend Tests

```bash
cd backend
pytest tests -v
```

---

# Code Quality

## Run flake8

```bash
flake8
```

## Run black

```bash
black .
```

---

# Personas

The system was designed around three primary personas:

## Lebo Xhosa
Farmer working in remote areas with poor connectivity who needs simple safe/unsafe water monitoring.

## Jack Wilshere
Environmental researcher analysing long-term trends and exporting datasets.

## George Weah
Public health officer monitoring contamination risks and prioritising alerts.

---

# Accessibility

The frontend includes:

- high-contrast support
- keyboard navigation support
- responsive layouts
- WCAG-aware colour choices
- accessible filtering and alerts

---

# Validation Features

The backend validates:

- impossible sensor readings
- invalid timestamps
- duplicate readings
- invalid alert flags
- status mismatches
- faulty sensor values

Faulty readings are stored with:

```text
sensor_fault = True
fault_reason = "..."
```

This preserves traceability without polluting dashboard calculations.

---

# Continuous Integration

GitHub Actions automatically runs:

- pytest
- formatting checks
- linting validation

on pushes and pull requests.

---