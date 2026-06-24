DRHP_ANALYSIS_PROMPT = """
You are a senior Investment Banking analyst specialising in cross-border capital markets.
Your clients include FPIs, NRIs, family offices, and institutional investors.

Analyse this DRHP (Draft Red Herring Prospectus) and return ONLY a valid JSON object.
No explanation, no markdown, just raw JSON.

JSON structure to return:
{{
  "company": {{
    "name": "Full company name",
    "industry": "Sector",
    "ipo_size_cr": 0,
    "price_band": "Rs X-Y"
  }},
  "financials": {{
    "revenue": [
      {{"year": "FY22", "value_cr": 0}},
      {{"year": "FY23", "value_cr": 0}},
      {{"year": "FY24", "value_cr": 0}}
    ],
    "pat": [
      {{"year": "FY22", "value_cr": 0}},
      {{"year": "FY23", "value_cr": 0}},
      {{"year": "FY24", "value_cr": 0}}
    ],
    "ebitda_margin_pct": 0,
    "debt_equity_ratio": 0,
    "roce_pct": 0
  }},
  "promoters": [
    {{
      "name": "Full name",
      "shareholding_pct": 0,
      "pledged_pct": 0,
      "concerns": ["concern 1", "concern 2"]
    }}
  ],
  "risk_factors": [
    {{
      "category": "financial or regulatory or operational or market",
      "description": "Clear risk description",
      "severity": "high or medium or low"
    }}
  ],
  "red_flags": [
    {{
      "type": "Short flag name",
      "description": "Why this is a red flag"
    }}
  ],
  "fpi_notes": [
    {{
      "type": "positive or caution or negative",
      "text": "Note for FPI or NRI or family office investors"
    }}
  ],
  "dd_score": {{
    "overall": 0,
    "financials": 0,
    "governance": 0,
    "business_quality": 0,
    "risk_level": "high or medium or low",
    "investment_verdict": "Avoid or Cautious or Neutral or Accumulate or Strong Buy"
  }},
  "analyst_summary": "3-4 sentences for a foreign investor. What company does, financial health, biggest risk, recommendation."
}}

Scoring guide:
- Score each section 0 to 100
- Financials: profitability, margins, debt, cash flow
- Governance: promoter pledging, board independence, related party deals
- Business quality: market position, moat, sector tailwinds
- Overall: weighted average, governance weighted most heavily
- Risk level: high if score below 45, medium if 45-65, low if above 65

DRHP TEXT:
{drhp_text}
"""