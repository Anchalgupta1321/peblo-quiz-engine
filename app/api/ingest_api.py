from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import IngestionResponse
from app.models import SourceDocuments, ContentChunks
from app.ingestion.pdf_parser import extract_text_from_pdf
from app.ingestion.chunker import chunk_text
import uuid

router = APIRouter()

@router.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads a PDF, extracts text, chunks it, and saves it into DB."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    # Read PDF text
    content = await file.read()
    text = extract_text_from_pdf(content)
    
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
    
    return IngestionResponse(
        message="Document ingested successfully.",
        source_id=source_id,
        chunks_extracted=len(chunks_data)
    )
