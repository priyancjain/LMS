"""
Seed a flow with multiple sample questions for testing.
Run this script: python seed_flow.py
"""

from models import create_flow, create_question

# Create a flow
flow = create_flow(
    title="Python Fundamentals Quiz",
    created_by="teacher@example.com"
)

print(f"✓ Created flow: {flow.title}")
print(f"  Flow ID: {flow.flow_id}\n")

# Define questions for the flow
questions_data = [
    {
        "difficulty": "easy",
        "question_text": "What is the output of print(2 ** 3)?",
        "options": ["6", "8", "9", "5"],
        "correct_answer": "8",
        "hint_text": "** is the exponentiation operator in Python"
    },
    {
        "difficulty": "easy",
        "question_text": "Which of the following is a mutable data type in Python?",
        "options": ["tuple", "string", "list", "frozenset"],
        "correct_answer": "list",
        "hint_text": "Mutable means it can be changed after creation"
    },
    {
        "difficulty": "medium",
        "question_text": "What is the output of len('hello')?",
        "options": ["4", "5", "6", "Error"],
        "correct_answer": "5",
        "hint_text": "len() returns the number of characters in a string"
    },
    {
        "difficulty": "medium",
        "question_text": "Which method removes and returns the last item from a list?",
        "options": ["remove()", "delete()", "pop()", "shift()"],
        "correct_answer": "pop()",
        "hint_text": "pop() is used to remove items from the end of a list"
    },
    {
        "difficulty": "medium",
        "question_text": "What is the result of 10 // 3 in Python?",
        "options": ["3.33", "3", "4", "Error"],
        "correct_answer": "3",
        "hint_text": "// is the floor division operator"
    },
    {
        "difficulty": "hard",
        "question_text": "What does the lambda keyword do in Python?",
        "options": [
            "Defines a regular function",
            "Creates an anonymous function",
            "Declares a variable",
            "Imports a module"
        ],
        "correct_answer": "Creates an anonymous function",
        "hint_text": "lambda is used to create small unnamed functions"
    },
    {
        "difficulty": "hard",
        "question_text": "What is the output of [x**2 for x in range(3)]?",
        "options": ["[0, 1, 4]", "[1, 2, 3]", "[0, 1, 2]", "[1, 4, 9]"],
        "correct_answer": "[0, 1, 4]",
        "hint_text": "List comprehension: range(3) gives [0, 1, 2], then square each"
    },
    {
        "difficulty": "hard",
        "question_text": "What is a decorator in Python?",
        "options": [
            "A way to add Christmas ornaments to code",
            "A function that modifies another function or class",
            "A type of comment",
            "A loop statement"
        ],
        "correct_answer": "A function that modifies another function or class",
        "hint_text": "Decorators are applied with @ symbol and enhance functions"
    },
]

# Create questions
for i, q in enumerate(questions_data, 1):
    question = create_question(
        flow_id=flow.flow_id,
        difficulty=q["difficulty"],
        question_text=q["question_text"],
        options=q["options"],
        correct_answer=q["correct_answer"],
        hint_text=q["hint_text"],
    )
    print(f"✓ Created question {i}: {q['question_text'][:50]}...")

print(f"\n✅ Successfully created flow '{flow.title}' with {len(questions_data)} questions!")
print(f"Flow ID: {flow.flow_id}")
