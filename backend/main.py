from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "workfocus.sqlite3"

app = FastAPI(
    title="WorkFocus MVP API",
    version="0.1.0",
    description="Small backend for the WorkFocus interactive demo.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8088",
        "http://localhost:3000",
        "https://kang9863.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SessionStart(BaseModel):
    title: str = "Focus session"


class EventCreate(BaseModel):
    session_id: int | None = None
    event_type: str = Field(pattern="^(focus|smartphone|away|drowsy|end)$")
    description: str = ""
    duration_seconds: int | None = None


class MeetingCreate(BaseModel):
    title: str
    text: str


class SearchRequest(BaseModel):
    question: str


class TodoCreate(BaseModel):
    text: str
    owner: str = ""


class TodoUpdate(BaseModel):
    done: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def init_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                duration_seconds INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                duration_seconds INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            );

            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                summary TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                owner TEXT NOT NULL DEFAULT '',
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            """
        )


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "workfocus-api", "db": str(DB_PATH.name)}


@app.post("/api/sessions")
def start_session(payload: SessionStart) -> dict:
    with db() as conn:
        cursor = conn.execute(
            "INSERT INTO sessions (title, started_at) VALUES (?, ?)",
            (payload.title, utc_now()),
        )
        return {"id": cursor.lastrowid, "title": payload.title, "started_at": utc_now()}


@app.get("/api/sessions")
def list_sessions() -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM sessions ORDER BY id DESC").fetchall()
        return [row_to_dict(row) for row in rows]


@app.post("/api/sessions/{session_id}/stop")
def stop_session(session_id: int) -> dict:
    ended_at = utc_now()
    with db() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="session not found")

        started_at = datetime.fromisoformat(row["started_at"])
        duration = int((datetime.fromisoformat(ended_at) - started_at).total_seconds())
        conn.execute(
            "UPDATE sessions SET ended_at = ?, duration_seconds = ? WHERE id = ?",
            (ended_at, duration, session_id),
        )
        return {"id": session_id, "ended_at": ended_at, "duration_seconds": duration}


@app.post("/api/events")
def create_event(payload: EventCreate) -> dict:
    with db() as conn:
        if payload.session_id is not None:
            session = conn.execute("SELECT id FROM sessions WHERE id = ?", (payload.session_id,)).fetchone()
            if session is None:
                raise HTTPException(status_code=404, detail="session not found")

        created_at = utc_now()
        cursor = conn.execute(
            """
            INSERT INTO events (session_id, event_type, description, duration_seconds, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.session_id,
                payload.event_type,
                payload.description,
                payload.duration_seconds,
                created_at,
            ),
        )
        return {
            "id": cursor.lastrowid,
            "session_id": payload.session_id,
            "event_type": payload.event_type,
            "description": payload.description,
            "duration_seconds": payload.duration_seconds,
            "created_at": created_at,
        }


@app.get("/api/events")
def list_events(session_id: int | None = None) -> list[dict]:
    query = "SELECT * FROM events"
    params: tuple = ()
    if session_id is not None:
        query += " WHERE session_id = ?"
        params = (session_id,)
    query += " ORDER BY id DESC LIMIT 100"
    with db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [row_to_dict(row) for row in rows]


@app.post("/api/meetings/summarize")
def summarize_meeting(payload: MeetingCreate) -> dict:
    summary, actions = summarize_text(payload.text)
    return {"title": payload.title, "summary": summary, "actions": actions}


@app.post("/api/meetings")
def create_meeting(payload: MeetingCreate) -> dict:
    summary, actions = summarize_text(payload.text)
    created_at = utc_now()
    with db() as conn:
        cursor = conn.execute(
            "INSERT INTO meetings (title, text, summary, created_at) VALUES (?, ?, ?, ?)",
            (payload.title, payload.text, summary, created_at),
        )
        return {
            "id": cursor.lastrowid,
            "title": payload.title,
            "text": payload.text,
            "summary": summary,
            "actions": actions,
            "created_at": created_at,
        }


@app.get("/api/meetings")
def list_meetings() -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM meetings ORDER BY id DESC").fetchall()
        return [row_to_dict(row) for row in rows]


@app.post("/api/search")
def search(payload: SearchRequest) -> dict:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    with db() as conn:
        meetings = conn.execute("SELECT title, text AS body FROM meetings ORDER BY id DESC").fetchall()
        events = conn.execute(
            "SELECT event_type AS title, description AS body FROM events ORDER BY id DESC LIMIT 30"
        ).fetchall()

    docs = [
        {"title": "집중 모니터링", "body": "웹캠 프레임을 분석해 집중, 자리 이탈, 스마트폰 사용, 졸림 이벤트를 기록합니다."},
        {"title": "회의 기록", "body": "회의 메모를 저장하고 핵심 요약과 다음 액션 아이템을 추출합니다."},
        {"title": "AI 검색", "body": "저장된 회의록과 이벤트 기록을 검색해 질문에 관련된 근거를 제공합니다."},
    ]
    docs.extend(row_to_dict(row) for row in meetings)
    docs.extend(row_to_dict(row) for row in events)

    terms = [term.lower() for term in question.split()]
    ranked = sorted(
        docs,
        key=lambda doc: sum(term in f"{doc['title']} {doc['body']}".lower() for term in terms),
        reverse=True,
    )
    sources = ranked[:3]
    answer = " ".join(source["body"] for source in sources)
    return {"question": question, "answer": answer, "sources": sources}


@app.post("/api/todos")
def create_todo(payload: TodoCreate) -> dict:
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    created_at = utc_now()
    with db() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (text, owner, created_at) VALUES (?, ?, ?)",
            (payload.text, payload.owner, created_at),
        )
        return {
            "id": cursor.lastrowid,
            "text": payload.text,
            "owner": payload.owner,
            "done": False,
            "created_at": created_at,
        }


@app.get("/api/todos")
def list_todos() -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
        return [{**row_to_dict(row), "done": bool(row["done"])} for row in rows]


@app.patch("/api/todos/{todo_id}")
def update_todo(todo_id: int, payload: TodoUpdate) -> dict:
    with db() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="todo not found")
        conn.execute("UPDATE todos SET done = ? WHERE id = ?", (int(payload.done), todo_id))
        return {"id": todo_id, "done": payload.done}


@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int) -> dict:
    with db() as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="todo not found")
        return {"deleted": True, "id": todo_id}


def summarize_text(text: str) -> tuple[str, list[str]]:
    sentences = [part.strip() for part in text.replace("\n", ". ").split(".") if part.strip()]
    keywords = ("다음", "작업", "구현", "배포", "확인", "정리", "추가", "수정")

    ranked = sorted(
        sentences,
        key=lambda sentence: sum(keyword in sentence for keyword in keywords) + min(len(sentence) / 100, 1),
        reverse=True,
    )
    summary = "\n".join(f"- {sentence}" for sentence in ranked[:3]) or "- 요약할 내용이 없습니다."
    actions = [sentence for sentence in sentences if any(keyword in sentence for keyword in keywords)]
    return summary, actions[:5]
