# CloudLaunch — Phase 1: Application Development

CloudLaunch is a small FastAPI application with a responsive browser dashboard. This phase monitors **the local computer running the app**. The CPU, memory, and disk values are collected with `psutil`; they are not AWS or CloudWatch metrics. No AWS connection or credentials are used.

## Project layout

```text
CloudLaunch/
├── backend/
│   └── main.py        # FastAPI routes, local metric collection, error handling
├── frontend/
│   ├── index.html     # Dashboard structure and metric cards
│   ├── styles.css     # Responsive dark dashboard styling
│   └── app.js         # API requests, formatting, and five-second refresh
├── .gitignore
├── README.md
└── requirements.txt
```

## Start on Windows

Open a terminal in the project folder, activate the existing virtual environment, then start Uvicorn:

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload
```

If PowerShell blocks activation, run the interpreter directly:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Open <http://127.0.0.1:8000/> to view the dashboard. The interactive API documentation is at <http://127.0.0.1:8000/docs>.

## Endpoints

- `GET /` — serves the dashboard.
- `GET /health` — simple liveness response.
- `GET /api/status` — app state, uptime, and the declared local metrics source.
- `GET /api/metrics` — current local CPU, memory, and system-drive usage.

## Try the API

In a second PowerShell terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/status
Invoke-RestMethod http://127.0.0.1:8000/api/metrics
```

## How it works

`backend/main.py` defines the FastAPI app. `collect_metrics()` reads the CPU percentage, virtual memory, and disk usage through `psutil`; the disk path is the root of the drive where the app is running. `/api/metrics` turns expected operating-system or `psutil` collection failures into an HTTP 503 response. The global exception handler logs unexpected server errors and returns a generic HTTP 500 message without leaking internal details.

`frontend/index.html` provides accessible dashboard sections and cards. `frontend/styles.css` adapts the three-card layout to narrow screens. `frontend/app.js` requests the metrics and status endpoints, formats byte counts for display, and repeats the request every five seconds. If a request fails, it shows an error banner and retries on the next interval.

## Basic verification

With the virtual environment active, compile the backend and check the API using FastAPI's test client:

```powershell
python -m compileall backend
python -c "from fastapi.testclient import TestClient; from backend.main import app; c=TestClient(app); assert c.get('/').status_code == 200; assert c.get('/health').json()['status'] == 'ok'; assert c.get('/api/status').json()['metrics_source'] == 'local machine'; m=c.get('/api/metrics'); assert m.status_code == 200 and m.json()['source'] == 'local machine'; print('Basic checks passed')"
```

If dependencies need to be recreated later, install them with `python -m pip install -r requirements.txt` inside the virtual environment.
