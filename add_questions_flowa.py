#!/usr/bin/env python3
"""
Create a flow named 'flowa' (if it doesn't exist) and add at least 10 questions
with a mix of easy, medium, and hard difficulties.
Run: ./venv/bin/python add_questions_flowa.py
"""
import sqlite3
import uuid
from datetime import datetime
import json

DB_PATH = "poc.db"
TEACHER_EMAIL = "jnpriyanshipragya@gmail.com"

QUESTIONS = [
    # Easy (4)
    ("What is the output of print(1+1)?", "2", ["11", "1", "error"], "easy", "Simple addition."),
    ("Which data type is used to store text in Python?", "str", ["int", "bool", "list"], "easy", "Strings hold text."),
    ("What does HTML stand for?", "HyperText Markup Language", ["HighText Markup Language", "Hyperlinks and Text Markup Language", "Home Tool Markup Language"], "easy", "HTML structures web pages."),
    ("Which HTTP method is typically used to retrieve data?", "GET", ["POST", "PUT", "DELETE"], "easy", "GET retrieves resources."),
    # Medium (3)
    ("What is the average time complexity of binary search?", "O(log n)", ["O(n)", "O(1)", "O(n log n)"], "medium", "Binary search halves the search space."),
    ("Which data structure uses FIFO order?", "Queue", ["Stack", "Tree", "Graph"], "medium", "Queue is First-In-First-Out."),
    ("In SQL, which clause is used to filter rows?", "WHERE", ["GROUP BY", "ORDER BY", "HAVING"], "medium", "WHERE filters rows before grouping."),
    # Hard (3)
    ("What is the time complexity of Merge Sort?", "O(n log n)", ["O(n^2)", "O(n)", "O(log n)"], "hard", "Merge sort divides and merges."),
    ("What is the purpose of a mutex in concurrent programming?", "To ensure mutual exclusion for shared resources", ["To speed up execution", "To duplicate data", "To schedule tasks"], "hard", "Mutex prevents race conditions."),
    ("What does CAP theorem state?", "A distributed system can only have two of: Consistency, Availability, Partition tolerance", ["It ensures data encryption", "It describes sorting algorithms", "It applies only to SQL databases"], "hard", "CAP describes trade-offs in distributed systems."),
]


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def find_flow_by_title(title):
    with _connect() as conn:
        row = conn.execute("SELECT flow_id, title, created_by FROM flows WHERE title = ?", (title,)).fetchone()
        if row:
            return row[0]
    return None


def create_flow(title, created_by):
    flow_id = uuid.uuid4().hex
    created_at = datetime.now().isoformat()
    with _connect() as conn:
        conn.execute("INSERT INTO flows (flow_id, title, created_by, created_at) VALUES (?, ?, ?, ?)", (flow_id, title, created_by, created_at))
        conn.commit()
    return flow_id


def create_question(flow_id, difficulty, question_text, options, correct_answer, hint_text):
    question_id = uuid.uuid4().hex
    created_at = datetime.now().isoformat()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO questions (question_id, flow_id, difficulty, question_text, options_json, correct_answer, hint_text, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (question_id, flow_id, difficulty, question_text, json.dumps(options), correct_answer, hint_text, created_at),
        )
        conn.commit()
    return question_id


def main():
    title = "flowa"
    flow_id = find_flow_by_title(title)
    if not flow_id:
        flow_id = create_flow(title, TEACHER_EMAIL)
        print(f"Created flow '{title}' with id {flow_id}")
    else:
        print(f"Found existing flow '{title}' with id {flow_id}")

    # Count existing questions for this flow
    with _connect() as conn:
        cur = conn.execute("SELECT COUNT(*) as c FROM questions WHERE flow_id = ?", (flow_id,))
        count = cur.fetchone()[0]
    print(f"Existing questions in flow: {count}")

    # Add questions if less than 10
    added = 0
    for q in QUESTIONS:
        if count + added >= 10:
            break
        question_text, correct, incorrect_list, difficulty, hint = q
        options = [correct] + incorrect_list
        create_question(flow_id, difficulty, question_text, options, correct, hint)
        added += 1

    print(f"Added {added} questions to flow '{title}'.")

if __name__ == '__main__':
    main()
