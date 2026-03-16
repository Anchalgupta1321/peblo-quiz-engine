from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import StudentAnswerSubmit, AnswerResponse
from app.models import Questions, StudentAnswers
from app.services.adaptive_engine import adjust_difficulty

router = APIRouter()

@router.post("/submit-answer", response_model=AnswerResponse)
def submit_answer(ans: StudentAnswerSubmit, db: Session = Depends(get_db)):
    """Submit an answer to a question. Grading algorithm calculates the adaptive learning curve."""
    question = db.query(Questions).filter(Questions.id == ans.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    is_correct = (str(ans.selected_answer).strip().lower() == str(question.answer).strip().lower())
    
    record = StudentAnswers(
        student_id=ans.student_id,
        question_id=ans.question_id,
        selected_answer=ans.selected_answer,
        is_correct=is_correct
    )
    db.add(record)
    db.commit()
    
    # Adapt to performance logic!
    next_diff = adjust_difficulty(question.difficulty, is_correct)
    
    return AnswerResponse(
        is_correct=is_correct,
        correct_answer=question.answer if not is_correct else "",
        original_difficulty=question.difficulty,
        next_recommended_difficulty=next_diff,
        source_chunk_id=question.source_chunk_id
    )
