from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
from pdf_extractor import extract_text_from_pdf, extract_text_from_txt
from analyzer import analyze_drhp
from report_generator import generate_pdf_report

app = FastAPI(
    title="IPO Due Diligence Bot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # Step 1 — validate file type
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF or TXT files accepted")

    # Step 2 — read file bytes
    file_bytes = await file.read()

    if len(file_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 15MB.")

    print(f"[main] Received: {file.filename} ({len(file_bytes):,} bytes)")

    # Step 3 — extract text
    if file.filename.endswith(".pdf"):
        extracted = extract_text_from_pdf(file_bytes)
    else:
        extracted = extract_text_from_txt(file_bytes)

    print(f"[main] Extracted {extracted['char_count']:,} chars from {extracted['page_count']} pages")

    if extracted["char_count"] < 500:
        raise HTTPException(status_code=422, detail="File appears empty or is a scanned image. Text extraction failed.")

    # Step 4 — run AI analysis
    analysis = analyze_drhp(extracted["chunks"])

    # Step 5 — attach metadata and return
    analysis["_meta"] = {
        "filename": file.filename,
        "pages": extracted["page_count"],
        "chars_extracted": extracted["char_count"]
    }

    return JSONResponse(content=analysis)


@app.post("/generate-report")
async def generate_report(analysis: dict):
    pdf_bytes = generate_pdf_report(analysis)

    company_name = analysis.get("company", {}).get("name", "IPO").replace(" ", "_")
    filename = f"DD_Report_{company_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/health")
async def health():
    return {"status": "ok"}