# CloudLaunch

CloudLaunch is a FastAPI application with a responsive browser dashboard. Phase 1 provides local system monitoring. Phase 2 packages the existing application as a Docker image and provides a Docker Compose workflow.

The CPU, memory, and disk values come from `psutil` inside the running process. When the app runs in Docker, those values reflect what the container's operating system environment exposes; they are not AWS or CloudWatch metrics. No AWS connection or credentials are used.

The displayed metrics source is configurable with `CLOUDLAUNCH_METRICS_SOURCE`. Direct local execution defaults to `local machine`; Docker Compose sets it to `Docker container`. Set the variable yourself to change the label for another execution environment.

## Project layout

```text
CloudLaunch/
├── backend/main.py       # FastAPI routes, local metric collection, error handling
├── frontend/             # Dashboard structure, styling, and browser code
├── Dockerfile            # Container image definition
├── compose.yaml          # Local Docker Compose service
├── .dockerignore         # Excludes local and source-control files from the build context
└── requirements.txt
```

## Run with Docker Compose

Install Docker Desktop (Windows/macOS) or Docker Engine with the Compose plugin (Linux), then run these commands from the repository root:

```sh
docker compose up --build -d
```

Open <http://localhost:8000/>. The interactive API documentation is at <http://localhost:8000/docs>.

To use another host port, set `CLOUDLAUNCH_PORT` before starting Compose:

```powershell
$env:CLOUDLAUNCH_PORT = "8080"
docker compose up --build -d
```

```sh
CLOUDLAUNCH_PORT=8080 docker compose up --build -d
```

The app will then be available at <http://localhost:8080/>. Check the service and health state with:

```sh
docker compose ps
docker compose logs -f cloudlaunch
```

Stop and remove the container with:

```sh
docker compose down
```

## Build and run with Docker directly

```sh
docker build -t cloudlaunch:local .
docker run --rm -p 8000:8000 cloudlaunch:local
```

To customize the displayed source when running the image directly, pass the environment variable:

```sh
docker run --rm -p 8000:8000 -e CLOUDLAUNCH_METRICS_SOURCE="Docker container" cloudlaunch:local
```

## Run without Docker on Windows

Activate the existing virtual environment and start Uvicorn:

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload
```

If PowerShell blocks activation, run the interpreter directly:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

## Endpoints

- `GET /` — serves the dashboard.
- `GET /health` — liveness response, also used by the Docker health check.
- `GET /api/status` — app state, uptime, and the declared metrics source.
- `GET /api/metrics` — current CPU, memory, and system-drive usage visible to the process.

`backend/main.py` defines the FastAPI app. `collect_metrics()` reads CPU percentage, virtual memory, and disk usage through `psutil`. The API maps expected metric collection failures to HTTP 503, and unexpected server errors to a generic HTTP 500 response.

The frontend requests metrics and status every five seconds. If a request fails, it displays an error banner and retries on the next interval.

## Dependencies

Install Python dependencies with:

```sh
python -m pip install -r requirements.txt
```
