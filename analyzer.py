
import os
import json
import re
from functools import lru_cache

from groq import Groq
from dotenv import load_dotenv

from prompts import DRHP_ANALYSIS_PROMPT


load_dotenv()

MAX_INPUT_CHARS = 80000


@lru_cache(maxsize=1)
def get_groq_client():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY environment variable is missing."
        )

    return Groq(api_key=api_key)


def analyze_drhp(text_chunks):

    if not text_chunks:
        raise ValueError("No extracted text available.")

    # Keep analysis input within the configured limit
    drhp_text = "\n\n".join(text_chunks)

    drhp_text = drhp_text[:MAX_INPUT_CHARS]

    prompt = DRHP_ANALYSIS_PROMPT.format(
        drhp_text=drhp_text
    )

    print(
        f"[analyzer] Sending {len(drhp_text):,} characters to Groq..."
    )

    client = get_groq_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    raw_response = response.choices[0].message.content

    if not raw_response:
        raise ValueError("Groq returned an empty response.")

    print(
        f"[analyzer] Response received ({len(raw_response)} characters)"
    )

    return parse_response(raw_response)


def parse_response(raw):

    cleaned = raw.strip()

    # Remove Markdown JSON code fences
    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    try:
        analysis = json.loads(cleaned)

        if not isinstance(analysis, dict):
            raise ValueError("Expected a JSON object.")

        return analysis

    except (json.JSONDecodeError, ValueError) as error:

        print(
            f"[analyzer] JSON parsing failed: {error}"
        )

        return {
            "error": "Could not parse analysis",
            "company": {
                "name": "Parse Error",
                "industry": "Unknown"
            },
            "dd_score": {
                "overall": 0,
                "risk_level": "high",
                "investment_verdict": "Error"
            },
            "analyst_summary":
                "Analysis failed. Please try again."
        }
