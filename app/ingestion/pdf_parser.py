import io
from pypdf import PdfReader

def extract_text_from_pdf(file_content: bytes) -> tuple:
    """Extracts text and page count from a given PDF file content."""
    reader = PdfReader(io.BytesIO(file_content))
    text = ""
    page_count = len(reader.pages)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text, page_count
