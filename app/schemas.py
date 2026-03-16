from pydantic import BaseModel
from typing import List, Optional

class ChunkBase(BaseModel):
    id: str
    source_id: str
    chunk_text: str
    topic: Optional[str] = None

class ChunkOut(ChunkBase):
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    id: str
    source_chunk_id: str
    type: str # MCQ, True/False, Fill in the blank
    question: str
    options: List[str]
    answer: str
    difficulty: str

class QuestionOut(QuestionBase):
    class Config:
        from_attributes = True

class StudentAnswerSubmit(BaseModel):
    student_id: str
    question_id: str
    selected_answer: str

class QuizGenerationRequest(BaseModel):
    source_id: str

class IngestionResponse(BaseModel):
    message: str
    source_id: str
    chunks_extracted: int

class QuizGenerationResponse(BaseModel):
    message: str
    questions_generated: int

class AnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    original_difficulty: str
    next_recommended_difficulty: str
