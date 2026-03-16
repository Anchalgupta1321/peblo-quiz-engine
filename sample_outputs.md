# Sample Outputs

This document showcases the outputs and typical responses from the Peblo Quiz Engine API.

## Database Schema (SQLAlchemy ORM Dump)
The following represents the structure created in SQLite:

```sql
CREATE TABLE documents (
    id VARCHAR NOT NULL, 
    filename VARCHAR, 
    PRIMARY KEY (id)
)

CREATE TABLE chunks (
    id VARCHAR NOT NULL, 
    document_id VARCHAR, 
    text TEXT, 
    grade INTEGER, 
    subject VARCHAR, 
    topic VARCHAR, 
    PRIMARY KEY (id), 
    FOREIGN KEY(document_id) REFERENCES documents (id)
)

CREATE TABLE questions (
    id VARCHAR NOT NULL, 
    chunk_id VARCHAR, 
    type VARCHAR, 
    question_text TEXT, 
    options TEXT, 
    answer VARCHAR, 
    difficulty VARCHAR, 
    PRIMARY KEY (id), 
    FOREIGN KEY(chunk_id) REFERENCES chunks (id)
)

CREATE TABLE student_answers (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
    student_id VARCHAR, 
    question_id VARCHAR, 
    selected_answer VARCHAR, 
    is_correct BOOLEAN, 
    FOREIGN KEY(question_id) REFERENCES questions (id)
)

CREATE TABLE student_proficiency (
    student_id VARCHAR NOT NULL, 
    topic VARCHAR NOT NULL, 
    score INTEGER, 
    PRIMARY KEY (student_id, topic)
)
```

## Example API Responses

### 1. Ingestion (`POST /ingest`)
```json
{
  "message": "Document ingested successfully. You can now generate quizzes from it.",
  "document_id": "422e11e0-76b6-45ef-891d-e9700b09d2a6",
  "chunks_extracted": 2
}
```

### 2. Quiz Generation (`POST /generate-quiz`)
```json
{
  "message": "Quiz generation complete.",
  "questions_generated": 4
}
```

### 3. Fetching Quizzes (`GET /quiz`) - Returns generated questions
```json
[
  {
    "id": "e4ed1d5a-669b-4ff4-bc58-7c858b90c7cb",
    "chunk_id": "422e11e0-76b6-45ef-891d-e9700b09d2a6_CH_1",
    "type": "MCQ",
    "question_text": "What is the main topic discussed in the text?",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Option A",
    "difficulty": "easy"
  },
  {
    "id": "0dfbd3d8-5cd4-4c59-8671-55e2d6bce775",
    "chunk_id": "422e11e0-76b6-45ef-891d-e9700b09d2a6_CH_1",
    "type": "True/False",
    "question_text": "The text provides information true or false?",
    "options": [
      "True",
      "False"
    ],
    "answer": "True",
    "difficulty": "medium"
  }
]
```

### 4. Submit Answer (`POST /submit-answer`) - Triggers Adaptive Logic
```json
// Example: Valid correct answer
{
  "is_correct": true,
  "correct_answer": "",
  "original_difficulty": "medium",
  "next_recommended_difficulty": "hard"
}

// Example: Incorrect answer
{
  "is_correct": false,
  "correct_answer": "Option A",
  "original_difficulty": "hard",
  "next_recommended_difficulty": "medium"
}
```
