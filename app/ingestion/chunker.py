def chunk_text(text: str, source_id: str, chunk_size=300):
    """Chunks text into segments of roughly `chunk_size` words."""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk_str = " ".join(words[i:i+chunk_size])
        chunk_id = f"{source_id}_CH_{len(chunks) + 1}"
        
        chunks.append({
            "id": chunk_id,
            "source_id": source_id,
            "chunk_text": chunk_str,
            "topic": None # Topic can be added via another LLM extraction step optionally
        })
        
    return chunks
