"""
Data model placeholders.

Persistence (SQLite/JSON) and domain models will be added later.
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel


DB_PATH = "poc.db"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS flows (
              flow_id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              created_by TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
              question_id TEXT PRIMARY KEY,
              flow_id TEXT NOT NULL,
              difficulty TEXT NOT NULL,
              question_text TEXT NOT NULL,
              options_json TEXT NOT NULL,
              correct_answer TEXT NOT NULL,
              hint_text TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(flow_id) REFERENCES flows(flow_id) ON DELETE CASCADE
            );
            """
        )


class FlowCreateRequest(BaseModel):
    title: str


class QuestionCreateRequest(BaseModel):
    flow_id: str
    difficulty: Literal["easy", "medium", "hard"]
    question_text: str
    options: List[str]
    correct_answer: str
    hint_text: str = ""


@dataclass(frozen=True)
class FlowRecord:
    flow_id: str
    title: str
    created_by: str
    created_at: str


@dataclass(frozen=True)
class QuestionRecord:
    question_id: str
    flow_id: str
    difficulty: str
    question_text: str
    options: List[str]
    correct_answer: str
    hint_text: str
    created_at: str


def create_flow(*, title: str, created_by: str) -> FlowRecord:
    flow_id = uuid.uuid4().hex
    created_at = _utc_now_iso()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO flows (flow_id, title, created_by, created_at) VALUES (?, ?, ?, ?)",
            (flow_id, title, created_by, created_at),
        )
        conn.commit()
    return FlowRecord(flow_id=flow_id, title=title, created_by=created_by, created_at=created_at)


def get_flow(flow_id: str) -> Optional[FlowRecord]:
    with _connect() as conn:
        row = conn.execute("SELECT flow_id, title, created_by, created_at FROM flows WHERE flow_id = ?", (flow_id,)).fetchone()
    if not row:
        return None
    return FlowRecord(
        flow_id=row["flow_id"],
        title=row["title"],
        created_by=row["created_by"],
        created_at=row["created_at"],
    )


def create_question(
    *,
    flow_id: str,
    difficulty: str,
    question_text: str,
    options: List[str],
    correct_answer: str,
    hint_text: str,
) -> QuestionRecord:
    question_id = uuid.uuid4().hex
    created_at = _utc_now_iso()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO questions (
              question_id, flow_id, difficulty, question_text, options_json, correct_answer, hint_text, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question_id,
                flow_id,
                difficulty,
                question_text,
                json.dumps(options),
                correct_answer,
                hint_text,
                created_at,
            ),
        )
        conn.commit()
    return QuestionRecord(
        question_id=question_id,
        flow_id=flow_id,
        difficulty=difficulty,
        question_text=question_text,
        options=options,
        correct_answer=correct_answer,
        hint_text=hint_text,
        created_at=created_at,
    )


def list_questions_for_flow(flow_id: str) -> List[QuestionRecord]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT question_id, flow_id, difficulty, question_text, options_json, correct_answer, hint_text, created_at
            FROM questions
            WHERE flow_id = ?
            ORDER BY created_at ASC
            """,
            (flow_id,),
        ).fetchall()

    questions: List[QuestionRecord] = []
    for row in rows:
        questions.append(
            QuestionRecord(
                question_id=row["question_id"],
                flow_id=row["flow_id"],
                difficulty=row["difficulty"],
                question_text=row["question_text"],
                options=json.loads(row["options_json"]),
                correct_answer=row["correct_answer"],
                hint_text=row["hint_text"],
                created_at=row["created_at"],
            )
        )
    return questions


def list_flows() -> List[FlowRecord]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT flow_id, title, created_by, created_at FROM flows ORDER BY created_at DESC"
        ).fetchall()

    flows: List[FlowRecord] = []
    for row in rows:
        flows.append(
            FlowRecord(
                flow_id=row["flow_id"],
                title=row["title"],
                created_by=row["created_by"],
                created_at=row["created_at"],
            )
        )
    return flows
