import os
import json
from openai import OpenAI
from typing import List

api_key = os.getenv("LLM_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def is_mock_mode():
    return client is None

def generate_questions_from_chunk(chunk_text: str, chunk_id: str) -> List[dict]:
    if is_mock_mode():
        return generate_mock_questions(chunk_text, chunk_id)
        
    prompt = f"""
You are an educational quiz generator.

Generate 3 quiz questions from the following content.

Content:
{chunk_text}

Rules:
- Include MCQ, True/False, Fill in the blank
- Provide answers
- Assign difficulty level (easy, medium, hard)
- Return ONLY a JSON list of dictionaries.

Example output:
[
  {{
    "question": "How many sides does a triangle have?",
    "type": "MCQ",
    "options": ["2","3","4","5"],
    "answer": "3",
    "difficulty": "easy"
  }}
]
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You output JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content
        
        # Clean markdown if present
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        questions = json.loads(content.strip())
        
        # Enforce list type
        if isinstance(questions, dict) and "questions" in questions:
            questions = questions["questions"]
            
        # Add source_chunk_id tracing
        for q in questions:
            q["source_chunk_id"] = chunk_id
            
        return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def generate_mock_questions(chunk_text: str, chunk_id: str) -> List[dict]:
    return [
        {
            "question": "What is the main topic discussed in the text?",
            "type": "MCQ",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A",
            "difficulty": "easy",
            "source_chunk_id": chunk_id
        }
    ]
