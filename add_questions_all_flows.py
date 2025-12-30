#!/usr/bin/env python3
"""
Add up to 10 questions for each existing flow in `poc.db`.
If a flow already has >=10 questions it will be skipped.
Generated questions are simple placeholders (easy/medium/hard mix).
Run: ./venv/bin/python add_questions_all_flows.py
"""
import sqlite3
import uuid
import json
from datetime import datetime

DB_PATH = "poc.db"

# Simple question templates for each difficulty
TEMPLATES = {
    "easy": [
        ("What does 1+1 equal?", "2", ["11", "1", "None"]),
        ("Which keyword starts a function in Python?", "def", ["func", "function", "lambda"]),
        ("HTML is used to build what?", "Web pages", ["Databases", "Operating Systems", "APIs"]),
    ],
    "medium": [
        ("What is the time complexity of binary search?", "O(log n)", ["O(n)", "O(1)", "O(n log n)"]),
        ("Which data structure uses LIFO ordering?", "Stack", ["Queue", "Tree", "Graph"]),
        ("SQL keyword to filter rows?", "WHERE", ["GROUP BY", "ORDER BY", "HAVING"]),
    ],
    "hard": [
        ("Time complexity of merge sort?", "O(n log n)", ["O(n^2)", "O(n)", "O(log n)"]),
        ("What does ACID stand for (databases)?", "Atomicity, Consistency, Isolation, Durability", ["Availability, Consistency, Integrity, Durability", "Atomicity, Consistency, Integrity, Durability", "Authentication, Consistency, Isolation, Durability"]),
        ("What problem do mutexes solve?", "Prevent race conditions on shared resources", ["Speed up IO", "Memory leak prevention", "Network routing"]),
    ],
}

DIFFICULTY_ORDER = ["easy", "medium", "hard"]


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def list_flows():
    with _connect() as conn:
        rows = conn.execute("SELECT flow_id, title FROM flows ORDER BY created_at DESC").fetchall()
        return [(r["flow_id"], r["title"]) for r in rows]


def count_questions(flow_id):
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) as c FROM questions WHERE flow_id = ?", (flow_id,)).fetchone()
        return row[0]


def add_question(flow_id, difficulty, question_text, options, correct_answer, hint_text=""):
    question_id = uuid.uuid4().hex
    created_at = datetime.now().isoformat()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO questions (question_id, flow_id, difficulty, question_text, options_json, correct_answer, hint_text, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (question_id, flow_id, difficulty, question_text, json.dumps(options), correct_answer, hint_text, created_at),
        )
        conn.commit()
    return question_id


def ensure_10_questions_per_flow():
    flows = list_flows()
    report = []
    for flow_id, title in flows:
        existing = count_questions(flow_id)
        to_add = max(0, 10 - existing)
        added = 0
        if to_add <= 0:
            report.append((flow_id, title, existing, added))
            continue

        # Add questions round-robin across difficulties
        template_iter = []
        for d in DIFFICULTY_ORDER:
            template_iter.extend([(d, q) for q in TEMPLATES[d]])

        idx = 0
        while added < to_add:
            difficulty, (qtext, correct, incorrects) = template_iter[idx % len(template_iter)]
            options = [correct] + incorrects
            add_question(flow_id, difficulty, qtext, options, correct, "Auto-generated question")
            added += 1
            idx += 1

        report.append((flow_id, title, existing, added))

    return report


if __name__ == '__main__':
    report = ensure_10_questions_per_flow()
    for flow_id, title, before, added in report:
        print(f"Flow '{title}' ({flow_id}): had {before} questions, added {added} -> now {before+added}")
