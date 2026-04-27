# Environment-Project

# Water Quality Monitoring Dashboard

A web application for monitoring water quality sensor data across multiple sites in South Africa. 
Built for farmers, environmental researchers, and public health officers to detect contamination risks and analyse trends.

## Tech Stack

**Backend:** Python, Flask, pandas  
**Frontend:** HTML, CSS, Javascript  
**Data:** CSV dataset — 200k+ sensor readings across multiple sites

## Setup

### Prerequisites
- Python 3.11+
- pip

### Installation

# Clone the repo
git clone https://github.com/your-repo-url

# Navigate to backend
cd backend

# Install production dependencies
pip install -r requirements.txt

# Install dev dependencies (linting, testing)
pip install -r requirements-dev.txt

# Install pre-commit hooks (required for all contributors)
pre-commit install

### Running the API
python app.py

The API will start at http://127.0.0.1:5000

## API Endpoints

| Method | Endpoint | Description | Persona |
|---|---|---|---|
| GET | /sites | Returns all unique site IDs | All |
| GET | /latest?site_id= | Most recent reading for a site | Lebo Xhosa |
| GET | /summary?site_id= | Latest key metrics for a site | Lebo Xhosa |
| GET | /timeseries | Aggregated readings over time | Jack Wilshere, George Weah |
| GET | /alerts | Alert events filtered by severity | Lebo Xhosa, George Weah |
| GET | /export | Download filtered data as CSV | Jack Wilshere |

Full parameter details in the Wiki.

## Project Structure

backend/
├── app.py              # Entry point — registers all route blueprints
├── config.py           # All constants and valid values
├── routes/             # HTTP route handlers — no business logic
├── services/           # Data loading, filtering, aggregation
├── validation/         # Input validation for all endpoints
└── tests/              # Pytest test suite

## Running Tests

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=term-missing

## Coding Standards

This project uses Black and Flake8 enforced via pre-commit hooks.
Line length: 100 characters.
Docstring format: Google style.
Naming: snake_case variables/functions, UPPER_SNAKE_CASE constants, PascalCase classes.

# Format code manually
black .

# Check for linting issues
flake8 .

Pre-commit hooks run both automatically before every commit.
Full standards documented in the Wiki.

## Contributing

- Never commit directly to main
- Create a feature branch for each user story
- Open a pull request and get one review before merging
- All PRs must pass Black and Flake8 before merge
- Reference the relevant GitHub issue number in your PR description