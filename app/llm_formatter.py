import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# laad .env vanuit project root
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")


def format_with_llm(intent: str, raw_text: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("[LLM FORMATTER ERROR] OPENAI_API_KEY ontbreekt")
        return None

    client = OpenAI(api_key=api_key)

    prompt = f"""
Je herschrijft feitelijke reisinfo voor een motorreis naar een kort, duidelijk en natuurlijk WhatsApp-antwoord in het Nederlands.

Regels:
- Verzin geen feiten.
- Gebruik alleen de info uit de input.
- Hou het kort en bruikbaar.
- Schrijf alsof je een praktische reisbuddy bent.
- Geen overdreven marketingtoon.
- Geen emoji tenzij het echt nuttig is.
- Voor hotel/route/highlights: maximaal ongeveer 5 regels.
- Voor briefing: compact, maar wel iets vloeiender.
- Voor advice: geef 3 korte, concrete tips of aandachtspunten.

Type antwoord: {intent}

Feitelijke input:
{raw_text}
""".strip()

    try:
        response = client.responses.create(
            model="gpt-5.4",
            input=prompt,
        )

        return response.output_text.strip()

    except Exception as e:
        print(f"[LLM FORMATTER ERROR] {e}")
        return None