import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# laad .env vanuit project root
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")


def parse_with_llm(user_input: str) -> dict | None:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("[LLM PARSER ERROR] OPENAI_API_KEY ontbreekt")
        return None

    client = OpenAI(api_key=api_key)

    prompt = f"""
Je krijgt een gebruikersvraag over een motorreis.

Bepaal:
1. intent: één van
- hotel
- highlights
- route
- briefing
- show_day
- set_day
- help
- unknown

2. day_reference: één van
- vandaag
- morgen
- dag_X
- none

3. set_day_value: een getal als de gebruiker expliciet de actieve dag wil zetten, anders null

Geef alleen geldige JSON terug in dit formaat:
{{
  "intent": "hotel",
  "day_reference": "vandaag",
  "set_day_value": null
}}

Gebruikersvraag:
{user_input}
""".strip()

    try:
        response = client.responses.create(
            model="gpt-5.4",
            input=prompt,
        )

        text = response.output_text.strip()
        return json.loads(text)

    except Exception as e:
        print(f"[LLM PARSER ERROR] {e}")
        return None


def resolve_llm_day(parsed: dict, current_day: int) -> int | None:
    day_ref = parsed.get("day_reference")

    if day_ref == "vandaag":
        return current_day
    if day_ref == "morgen":
        return current_day + 1
    if isinstance(day_ref, str) and day_ref.startswith("dag_"):
        try:
            return int(day_ref.split("_")[1])
        except Exception:
            return None

    return None