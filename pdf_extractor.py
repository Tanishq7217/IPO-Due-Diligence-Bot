
import io
import pdfplumber


CHUNK_SIZE = 60000
MAX_ANALYSIS_CHARS = 80000


def chunk_text(text, chunk_size=CHUNK_SIZE):

    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]


def extract_text_from_pdf(file_source):

    retained_text = []
    total_chars = 0

    if isinstance(file_source, bytes):
        file_source = io.BytesIO(file_source)

    with pdfplumber.open(file_source) as pdf:

        total_pages = len(pdf.pages)

        for page in pdf.pages:

            try:
                page_text = page.extract_text()

                if page_text:

                    total_chars += len(page_text)

                    remaining = (
                        MAX_ANALYSIS_CHARS -
                        sum(len(part) for part in retained_text)
                    )

                    if remaining > 0:
                        retained_text.append(
                            page_text[:remaining]
                        )

            finally:
                page.close()

    extracted_text = "\n\n".join(retained_text)

    chunks = chunk_text(extracted_text)

    return {
        "chunks": chunks,
        "page_count": total_pages,
        "char_count": total_chars
    }


def extract_text_from_txt(file_bytes):

    text = file_bytes.decode(
        "utf-8",
        errors="ignore"
    )

    retained_text = text[:MAX_ANALYSIS_CHARS]

    return {
        "chunks": chunk_text(retained_text),
        "page_count": 0,
        "char_count": len(text)
    }
