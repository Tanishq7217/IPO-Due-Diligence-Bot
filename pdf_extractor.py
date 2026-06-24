import pdfplumber
import io

def extract_text_from_pdf(file_bytes):
    text_pages = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        total_pages = len(pdf.pages)

        for i, page in enumerate(pdf.pages):
            page_text  = page.extract_text()
            if page_text:
                text_pages.append(page_text)

    full_text = "\n\n".join(text_pages)
    chunks = chunk_text(full_text)

    return{
        "full_text" : full_text,
        "chunks" : chunks,
        "page_count": total_pages,
        "char_count" : len(full_text)
    }

def chunk_text(text, chunk_size = 60000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

def extract_text_from_txt(file_bytes):
    text = file_bytes.decode("utf-8", errors="ignore")
    chunks = chunk_text(text)
    return {
        "full_text": text,
        "chunks": chunks,
        "page_count": 0,
        "char_count": len(text)
    }