# WorkFocus MVP Backend

Small FastAPI backend for the WorkFocus demo. It stores focus sessions, events, meeting notes, search data, and todos in SQLite.

## Live API

```text
https://workfocus-api.onrender.com
```

Health check:

```text
https://workfocus-api.onrender.com/api/health
```

API docs:

```text
https://workfocus-api.onrender.com/docs
```

## Run

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

Local API docs:

```text
http://localhost:8000/docs
```

## Notes

- Render Free services can sleep when inactive, so the first request may be slow.
- SQLite data on free hosting is good enough for demos, but not for production persistence.
- For production, move data to Postgres, Supabase, or Neon.

## Endpoints

- `GET /api/health`
- `POST /api/sessions`
- `POST /api/sessions/{id}/stop`
- `GET /api/sessions`
- `POST /api/events`
- `GET /api/events`
- `POST /api/meetings/summarize`
- `POST /api/meetings`
- `GET /api/meetings`
- `POST /api/search`
- `POST /api/todos`
- `GET /api/todos`
- `PATCH /api/todos/{id}`
- `DELETE /api/todos/{id}`
