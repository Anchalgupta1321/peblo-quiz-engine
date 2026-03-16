from sqlalchemy.orm import Session
from app import models
import json
import uuid

def is_duplicate(db: Session, question_text: str) -> bool:
    """Check for duplicate questions by literal string match.
       For a more robust solution, you would use sentence-transformers to generate embeddings 
       and check semantic similarity using pgvector or a vector store.
    """
    exists = db.query(models.Questions).filter(models.Questions.question == question_text).first()
    return bool(exists)

def save_generated_questions(db: Session, questions_data: list):
    """Saves generated generated questions into database avoiding duplicates."""
    stored = []
    for q in questions_data:
        # Deduplication check
        if is_duplicate(db, q['question']):
            continue
            
        options = q.get('options', [])
        question = models.Questions(
            id=str(uuid.uuid4()),
            source_chunk_id=q['source_chunk_id'],
            type=q.get('type', 'MCQ'),
            question=q['question'],
            options=json.dumps(options) if isinstance(options, list) else str(options),
            answer=str(q.get('answer', '')),
            difficulty=q.get('difficulty', 'medium')
        )
        db.add(question)
        stored.append(question)
        
    db.commit()
    return stored
