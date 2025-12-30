#!/usr/bin/env python3
"""
Create a sample learning flow in the database for testing.
"""
import sqlite3
import json
import uuid
from datetime import datetime

DB_PATH = "poc.db"

def create_sample_flow():
    """Create a sample flow with questions about Data Structures"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if flow already exists
    cursor.execute("SELECT flow_id FROM flows WHERE title = ?", ("Data Structures Fundamentals",))
    existing = cursor.fetchone()
    if existing:
        print(f"✓ Flow already exists with ID {existing[0]}")
        conn.close()
        return existing[0]
    
    # Generate flow ID
    flow_id = str(uuid.uuid4())
    
    # Insert flow
    cursor.execute("""
        INSERT INTO flows (flow_id, title, created_by, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        flow_id,
        "Data Structures Fundamentals",
        "jnpriyanshipragya@gmail.com",
        datetime.now().isoformat()
    ))
    conn.commit()
    
    # Sample questions with progressive difficulty
    questions = [
        {
            "content": "What is an array?",
            "correct": "A contiguous block of memory storing elements of the same type",
            "incorrect": [
                "A collection of unique elements",
                "A recursive data structure",
                "A tree-like structure with nodes"
            ],
            "difficulty": "1",
            "hint": "Think about how memory is allocated for a list of items.",
        },
        {
            "content": "What is the time complexity of accessing an element by index in an array?",
            "correct": "O(1) - Constant time",
            "incorrect": [
                "O(n) - Linear time",
                "O(log n) - Logarithmic time",
                "O(n²) - Quadratic time"
            ],
            "difficulty": "1",
            "hint": "Since arrays store elements in contiguous memory, accessing by index is direct.",
        },
        {
            "content": "What is a linked list?",
            "correct": "A data structure where elements are stored in nodes, with each node containing a reference to the next node",
            "incorrect": [
                "A contiguous block of memory",
                "A tree structure with multiple children",
                "A hash table implementation"
            ],
            "difficulty": "2",
            "hint": "Think about a chain where each link points to the next one.",
        },
        {
            "content": "What is the time complexity of inserting an element at the beginning of a linked list?",
            "correct": "O(1) - Constant time",
            "incorrect": [
                "O(n) - Linear time",
                "O(log n) - Logarithmic time",
                "O(n²) - Quadratic time"
            ],
            "difficulty": "2",
            "hint": "You only need to update pointers, not shift any elements.",
        },
        {
            "content": "What is a stack?",
            "correct": "A LIFO (Last In, First Out) data structure where elements are added and removed from the same end",
            "incorrect": [
                "A FIFO (First In, First Out) data structure",
                "A randomly accessible data structure",
                "A data structure with multiple levels of depth"
            ],
            "difficulty": "2",
            "hint": "Think of a stack of plates - you add and remove from the top.",
        },
        {
            "content": "What is the space complexity of a binary tree with n nodes?",
            "correct": "O(n) - Linear space",
            "incorrect": [
                "O(log n) - Logarithmic space",
                "O(1) - Constant space",
                "O(n²) - Quadratic space"
            ],
            "difficulty": "3",
            "hint": "Each node requires storage, and there are n nodes total.",
        },
        {
            "content": "What is the average time complexity of search in a balanced binary search tree?",
            "correct": "O(log n) - Logarithmic time",
            "incorrect": [
                "O(1) - Constant time",
                "O(n) - Linear time",
                "O(n log n) - Linearithmic time"
            ],
            "difficulty": "3",
            "hint": "A balanced BST eliminates half the remaining nodes with each comparison.",
        },
        {
            "content": "Which data structure would you use to implement a cache with LRU (Least Recently Used) eviction?",
            "correct": "Combination of HashMap and Doubly Linked List",
            "incorrect": [
                "Only an array",
                "Only a stack",
                "Only a queue"
            ],
            "difficulty": "3",
            "hint": "You need fast lookup and the ability to track insertion/access order.",
        }
    ]
    
    # Insert questions
    for i, q in enumerate(questions):
        question_id = str(uuid.uuid4())
        options = [q["correct"]] + q["incorrect"]
        options_json = json.dumps(options)
        
        cursor.execute("""
            INSERT INTO questions 
            (question_id, flow_id, question_text, options_json, correct_answer, difficulty, hint_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            question_id,
            flow_id,
            q["content"],
            options_json,
            q["correct"],
            q["difficulty"],
            q["hint"],
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Created flow 'Data Structures Fundamentals' with ID {flow_id}")
    print(f"✓ Added {len(questions)} questions")
    print(f"✓ Questions range from difficulty 1 (beginner) to 3 (advanced)")
    return flow_id

if __name__ == "__main__":
    try:
        create_sample_flow()
        print("\n✓ Sample flow created successfully!")
        print("✓ Visit https://lms-k2f0.onrender.com to log in and start learning")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
