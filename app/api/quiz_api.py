from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import QuizGenerationRequest, QuizGenerationResponse, QuestionOut
from app.models import ContentChunks, Questions
from app.llm.quiz_generator import generate_questions_from_chunk
from app.services.quiz_service import save_generated_questions
import json
from typing import List

router = APIRouter()

@router.post("/generate-quiz", response_model=QuizGenerationResponse)
def generate_quiz(req: QuizGenerationRequest, db: Session = Depends(get_db)):
    """Generates quiz questions from chunked contents in DB."""
    chunks = db.query(ContentChunks).filter(ContentChunks.source_id == req.source_id).all()
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for the given document.")
        
    total_generated = 0
    for chunk in chunks:
        # Prevent generation if already populated
        existing = db.query(Questions).filter(Questions.source_chunk_id == chunk.id).count()
        if existing > 0:
            continue
            
        # Send text to LLM service
        questions_data = generate_questions_from_chunk(chunk.chunk_text, chunk.id)
        if questions_data:
            # Service handles duplicates matching strings
            stored = save_generated_questions(db, questions_data)
            total_generated += len(stored)
            
    return QuizGenerationResponse(
        message="Quiz generation complete.",
        questions_generated=total_generated
    )

@router.get("/quiz", response_model=List[QuestionOut])
def get_quiz(topic: str = None, difficulty: str = None, db: Session = Depends(get_db)):
    """Retrieves generated questions using optional topic or difficulty query filters."""
    query = db.query(Questions)
    
    if topic:
        query = query.join(ContentChunks).filter(ContentChunks.topic.ilike(f"%{topic}%"))
        
    if difficulty:
        query = query.filter(Questions.difficulty == difficulty)
        
    questions = query.limit(10).all()
    
    result = []
    for q in questions:
        # safely parse options back to list format
        try:
            options_list = json.loads(q.options) if q.options else []
        except:
            options_list = []
            
        result.append(QuestionOut(
            id=q.id,
            source_chunk_id=q.source_chunk_id,
            type=q.type,
            question=q.question,
            options=options_list,
            answer=q.answer,
            difficulty=q.difficulty
        ))
        
    return result
