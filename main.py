
import os
import asyncio
import logging

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from pdf_extractor import extract_text_from_pdf, extract_text_from_txt
from analyzer import analyze_drhp
from report_generator import generate_pdf_report


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 15 * 1024 * 1024

# Allow only one heavy analysis at a time
analysis_semaphore = asyncio.Semaphore(1)


app = FastAPI(
    title="IPO Due Diligence Bot",
    version="1.0.0"
)


app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    try:
        # Step 1: Validate filename
        filename = file.filename or ""

        if not filename.lower().endswith((".pdf", ".txt")):
            raise HTTPException(
                status_code=400,
                detail="Only PDF or TXT files accepted"
            )

        # Step 2: Check upload size without reading the whole PDF
        file_size = file.size

        if file_size is None:
            file.file.seek(0, os.SEEK_END)
            file_size = file.file.tell()
            file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File too large. Max 15MB."
            )

        logger.info(
            "Received %s (%s bytes)",
            filename,
            file_size
        )

        # Step 3: Limit simultaneous heavy processing
        async with analysis_semaphore:

            # Step 4: Extract text
            if filename.lower().endswith(".pdf"):

                file.file.seek(0)

                extracted = await run_in_threadpool(
                    extract_text_from_pdf,
                    file.file
                )

            else:

                file.file.seek(0)

                file_bytes = await run_in_threadpool(
                    file.file.read,
                    MAX_FILE_SIZE + 1
                )

                if len(file_bytes) > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail="File too large. Max 15MB."
                    )

                extracted = extract_text_from_txt(file_bytes)

                del file_bytes

            logger.info(
                "Extracted %s characters from %s pages",
                extracted["char_count"],
                extracted["page_count"]
            )

            # Step 5: Validate extracted text
            if extracted["char_count"] < 500:
                raise HTTPException(
                    status_code=422,
                    detail="File appears empty or is a scanned image. Text extraction failed."
                )

            if not extracted["chunks"]:
                raise HTTPException(
                    status_code=422,
                    detail="No usable text found in the document."
                )

            # Step 6: AI analysis
            analysis = await run_in_threadpool(
                analyze_drhp,
                extracted["chunks"]
            )

            # Step 7: Attach metadata
            analysis["_meta"] = {
                "filename": filename,
                "pages": extracted["page_count"],
                "chars_extracted": extracted["char_count"]
            }

            return JSONResponse(content=analysis)

    except HTTPException:
        raise

    except Exception:
        logger.exception("Analysis failed")

        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Please check server logs."
        )

    finally:
        await file.close()


@app.post("/generate-report")
async def generate_report(analysis: dict):

    try:
        pdf_bytes = await run_in_threadpool(
            generate_pdf_report,
            analysis
        )

        company_name = (
            analysis.get("company", {})
            .get("name", "IPO")
            .replace(" ", "_")
        )

        filename = f"DD_Report_{company_name}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                f'attachment; filename="{filename}"'
            }
        )

    except Exception:
        logger.exception("Report generation failed")

        raise HTTPException(
            status_code=500,
            detail="Could not generate PDF report."
        )


@app.get("/health")
async def health():
    return {"status": "ok"}
