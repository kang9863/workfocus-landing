# WorkFocus MVP Backend

로그인 없이 바로 붙여볼 수 있는 WorkFocus 데모용 API입니다. SQLite에 집중 세션, 이벤트, 회의록, 투두를 저장합니다.

## Run

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

API 문서:

```text
http://localhost:8000/docs
```

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
