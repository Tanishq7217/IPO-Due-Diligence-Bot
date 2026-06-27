# IPO Due Diligence Bot 🏦

An AI-powered DRHP analysis tool that reduces manual due diligence time
from 3 days to 3 minutes. Upload any SEBI DRHP and get a structured
report covering financials, risk factors, promoter background, red flags,
and cross-border investor notes.

---

## Demo

<img width="953" height="731" alt="image" src="https://github.com/user-attachments/assets/1c7bb5b5-21a1-428a-b18b-3da2c0289e22" />


---

## Features

- **PDF ingestion** — uploads and extracts text from DRHP PDFs (200–400 pages)
- **AI analysis** — Llama 3.3 70B extracts structured data via Groq API
- **DD scoring** — 0–100 composite score across financials, governance, business quality
- **Red flag detection** — identifies promoter concerns, litigation, subsidy dependency
- **Cross-border investor notes** — FPI, NRI, family office specific insights
- **PDF report export** — professional report ready for client delivery

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| AI Model | Llama 3.3 70B via Groq API |
| PDF Extraction | pdfplumber |
| Report Generation | ReportLab |
| Frontend | HTML, CSS, Vanilla JS |

---

## Project Structure

ipo-dd-bot/

├── main.py              # FastAPI app — 3 REST endpoints

├── analyzer.py          # Groq AI analysis engine

├── pdf_extractor.py     # PDF text extraction and chunking

├── prompts.py           # Prompt engineering layer

├── report_generator.py  # PDF report generation

├── requirements.txt

└── frontend/

└── index.html       # Full UI — upload, processing, report

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Tanishq7217/IPO-Due-Diligence-Bot.git
cd IPO-Due-Diligence-Bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key
Create a `.env` file:

Get a free key at console.groq.com — no credit card needed.

### 4. Run
```bash
python -m uvicorn main:app --reload
```
Open `http://localhost:8000`

---

## How it works

1. User uploads a DRHP PDF
2. `pdf_extractor.py` reads and chunks the text (DRHPs are 200–400 pages)
3. `analyzer.py` sends the text to Llama 3.3 70B via Groq with a structured prompt
4. AI returns JSON with financials, risks, promoters, red flags, FPI notes
5. Frontend renders the report and user can download a PDF

---

## Sample Output

Tested on Ola Electric Mobility Ltd DRHP (2024):
- DD Score: 41/100
- Risk Level: HIGH
- Verdict: Cautious
- Red flags: Never profitable, subsidy dependency, dual-class shares
- FPI note: 100% FDI via automatic route permitted

---

*Not investment advice. For informational purposes only.*

