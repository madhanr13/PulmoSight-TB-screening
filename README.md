# PulmoSight

PulmoSight is a secure tuberculosis lung radiograph review workspace:

- Flask provides the protected API and image review service.
- The optional `frontend/` app provides a Vite + React client with the same teal/coral visual system.
- The web app includes authenticated case review, registration, dashboard, history, and report export views.

## Features

- Chest radiograph upload and validation
- Vite + React frontend with responsive auth and review screens
- Modern interface with a consistent teal/coral research aesthetic
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
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       └── styles.css
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
│   ├── login.html
│   └── register.html
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

## React frontend

Run the Flask API first, then in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. Vite proxies `/api` requests to Flask on port 5000.

The React app also supports a production build:

```powershell
npm run build
```

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
