from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import IngestionResponse
from app import models
from app.models import SourceDocuments, ContentChunks
from app.ingestion.pdf_parser import extract_text_from_pdf
from app.ingestion.chunker import chunk_text
import uuid
import re

def extract_metadata_from_filename(filename: str):
    grade = None
    subject = None
    
    # Try to find grade (e.g., grade4, grade 3)
    grade_match = re.search(r'grade\s*(\d+)', filename.lower())
    if grade_match:
        grade = f"Grade {grade_match.group(1)}"
        
    # Try to find subject (common keywords)
    subjects = ["science", "math", "english", "grammar", "history", "vocabulary"]
    for s in subjects:
        if s in filename.lower():
            subject = s.capitalize()
            break
            
    return grade, subject

router = APIRouter()

@router.delete("/reset-db")
def reset_db(db: Session = Depends(get_db)):
    """Wipes the database for testing purposes."""
    db.query(models.StudentAnswers).delete()
    db.query(models.Questions).delete()
    db.query(models.ContentChunks).delete()
    db.query(models.SourceDocuments).delete()
    db.commit()
    return {"message": "Database wiped successfully."}

@router.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads a PDF, extracts text, chunks it, and saves it into DB."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    # Read PDF text
    content = await file.read()
    text, pages = extract_text_from_pdf(content)
    
    # Store source document
    source_id = str(uuid.uuid4())
    doc = SourceDocuments(id=source_id, file_name=file.filename)
    db.add(doc)
    
    # Chunk strings and store them in DB
    chunks_data = chunk_text(text, source_id=source_id)
    for c in chunks_data:
        chunk = ContentChunks(
            id=c['id'],
            source_id=c['source_id'],
            chunk_text=c['chunk_text'],
            topic=c['topic']
        )
        db.add(chunk)
        
    db.commit()
    
    grade, subject = extract_metadata_from_filename(file.filename)
    
    return IngestionResponse(
        message="Document ingested successfully.",
        source_id=source_id,
        filename=file.filename,
        pages_count=pages,
        chunks_extracted=len(chunks_data),
        grade=grade,
        subject=subject
    )
