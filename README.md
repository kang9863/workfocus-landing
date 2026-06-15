# WorkFocus Demo

Interactive WorkFocus prototype with a static GitHub Pages frontend and a small local FastAPI backend.

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

Run the local API:

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

## Deployment

The frontend is ready for static hosting services such as GitHub Pages or Vercel. The backend needs a Python server such as Render, Railway, Fly.io, or a VPS.

### GitHub Pages

1. Open the repository settings.
2. Go to **Pages**.
3. Set the source to `main` and `/root`.
4. Save the settings.

### Vercel

1. Import this GitHub repository in Vercel.
2. Keep the default static site settings.
3. Deploy.
