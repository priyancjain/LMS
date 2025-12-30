"""
Test script to verify the flow and questions are working correctly.
Run: python test_flow.py
"""

import json
from models import list_flows, list_questions_for_flow

# Get all flows
flows = list_flows()
print("=" * 60)
print("AVAILABLE FLOWS")
print("=" * 60)

if not flows:
    print("❌ No flows found!")
    exit(1)

for flow in flows:
    print(f"\n📚 Flow: {flow.title}")
    print(f"   ID: {flow.flow_id}")
    print(f"   Created by: {flow.created_by}")
    print(f"   Created at: {flow.created_at}")
    
    # Get questions for this flow
    questions = list_questions_for_flow(flow.flow_id)
    print(f"   Questions: {len(questions)}")
    
    if questions:
        print("\n   Questions in this flow:")
        for i, q in enumerate(questions, 1):
            print(f"\n   [{i}] {q.question_text}")
            print(f"       Difficulty: {q.difficulty}")
            print(f"       Options: {', '.join(q.options)}")
            print(f"       Correct: {q.correct_answer}")
            if q.hint_text:
                print(f"       Hint: {q.hint_text}")

print("\n" + "=" * 60)
print(f"✅ Total flows: {len(flows)}")
for flow in flows:
    questions = list_questions_for_flow(flow.flow_id)
    print(f"   - {flow.title}: {len(questions)} questions")
print("=" * 60)
