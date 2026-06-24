import os
import json
from groq import Groq
from dotenv import load_dotenv
from prompts import DRHP_ANALYSIS_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROP_API_KEY"))


def analyze_drhp(text_chunks):
    # Use first chunk — covers the most critical sections of a DRHP
    drhp_text = text_chunks[0] if text_chunks else ""

    # If second chunk exists, add a portion of it too
    if len(text_chunks) > 1:
        drhp_text += "\n\n--- ADDITIONAL SECTIONS ---\n\n" + text_chunks[1][:20000]

    # Fill the prompt with the actual DRHP text
    prompt = DRHP_ANALYSIS_PROMPT.format(drhp_text=drhp_text)

    print(f"[analyzer] Sending {len(drhp_text):,} characters to Groq...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    raw_response = response.choices[0].message.content
    print(f"[analyzer] Response received ({len(raw_response)} characters)")

    # Parse the JSON response
    analysis = parse_response(raw_response)
    return analysis

def parse_response(raw):
    # Remove markdown code fences if model added them
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1])

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[analyzer] JSON parse error: {e}")
        # Return a safe error structure instead of crashing
        return {
            "error": "Could not parse analysis",
            "company": {"name": "Parse Error", "industry": "Unknown"},
            "dd_score": {"overall": 0, "risk_level": "high", "investment_verdict": "Error"},
            "analyst_summary": "Analysis failed. Please try again."
        }
