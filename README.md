# WorkFocus Demo

Interactive WorkFocus prototype with a static GitHub Pages frontend and a small FastAPI backend.

## Live URLs

Frontend:

```text
https://kang9863.github.io/workfocus-landing/
```

Backend:

```text
https://workfocus-api.onrender.com
```

Backend API docs:

```text
https://workfocus-api.onrender.com/docs
```

## Source

- `index.html`: static interactive frontend demo.
- `backend/`: FastAPI MVP backend with SQLite persistence.

## Frontend

The frontend runs directly on GitHub Pages:

```text
https://kang9863.github.io/workfocus-landing/
```

It also works locally with any static server.

```powershell
py -3.12 -m http.server 8088
```

Open:

```text
http://localhost:8088
```

## Backend

Production API is deployed on Render Free:

```text
https://workfocus-api.onrender.com
```

Health check:

```text
https://workfocus-api.onrender.com/api/health
```

Run the API locally:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

API docs:

```text
http://localhost:8000/docs
```

## How to Use

1. Open the frontend:

```text
https://kang9863.github.io/workfocus-landing/
```

2. Open backend docs when testing API calls:

```text
https://workfocus-api.onrender.com/docs
```

3. Use the API endpoints from the docs to create sessions, events, meetings, searches, and todos.

4. If the backend is slow on the first request, wait a bit and refresh. Render Free services can sleep when inactive.

## Deployment

The frontend is deployed with GitHub Pages. The backend is deployed with Render Free using `render.yaml`.

### GitHub Pages

1. Open the repository settings.
2. Go to **Pages**.
3. Set the source to `main` and `/root`.
4. Save the settings.

### Vercel

1. Import this GitHub repository in Vercel.
2. Keep the default static site settings.
3. Deploy.

### Render Backend

The backend is managed by the root `render.yaml`.

```yaml
services:
  - type: web
    name: workfocus-api
    runtime: python
    plan: free
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Pushing to `main` triggers Render sync/deploy.

## Update Workflow

```powershell
git add .
git commit -m "Update WorkFocus demo"
git push
```

After pushing:

- GitHub Pages updates the frontend.
- Render updates the backend if files under `backend/` or `render.yaml` changed.
