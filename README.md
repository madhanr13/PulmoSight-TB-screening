# PulmoSight

PulmoSight is a Flask-based tuberculosis lung radiograph screening interface built around a two-module research pipeline:

- `preprocessing.py` validates image uploads and prepares radiographs for model input.
- `ga_mobilenet.py` applies a MobileNet-inspired inference pipeline and tunes the classification threshold with a genetic algorithm.
- The web app includes a multi-page dashboard, case gallery, admin login, history, and report export views.

## Features

- Chest radiograph upload and validation
- MobileNet-style preprocessing pipeline
- GA-optimized decision threshold
- Modern multi-page interface with a consistent teal/coral research aesthetic
- Result history tracking in memory
- JSON export for session summaries
- Admin access screen for demonstration use

## Project structure

```text
PulmoSight/
├── app.py
├── ga_mobilenet.py
├── preprocessing.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── static/
│   ├── app.js
│   └── styles.css
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── methodology.html
│   ├── about.html
│   ├── gallery.html
│   ├── history.html
│   ├── reports.html
│   └── login.html
└── Data/
```

## Local setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py app.py
```

Open http://127.0.0.1:5000

## Environment configuration

Create a local `.env` file or export variables before running:

```powershell
$env:PULMOSIGHT_SECRET_KEY="your-secret-key"
$env:PULMOSIGHT_ADMIN_EMAIL="admin@pulmosight.ai"
$env:PULMOSIGHT_ADMIN_PASSWORD="admin123"
```

Default login credentials are shown above for local demo use only.

## Demo note

This project is intended for research support and prototype workflows only. It is not a medical device or a validated diagnostic system.

## Deployment readiness

This repository is organized for GitHub push usage with a standard Python ignore list, dependency manifest, and project documentation.
