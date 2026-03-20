from pathlib import Path
from fastapi import FastAPI, Form
from fastapi.responses import Response
from pydantic import BaseModel
from fastapi.responses import Response
from xml.sax.saxutils import escape
import datetime

from app.agent_service import answer_question
from xml.sax.saxutils import escape

app = FastAPI(title="Motortrip Agent API")


class AskRequest(BaseModel):
    question: str


def build_response(success: bool, data=None, error=None):
    return {
        "success": success,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "data": data,
        "error": error,
    }


@app.get("/")
def root():
    return build_response(
        success=True,
        data={"message": "Motortrip Agent API draait"},
    )


@app.get("/health")
def health():
    return build_response(
        success=True,
        data={"status": "ok"},
    )


@app.post("/ask")
def ask(request: AskRequest):
    project_root = Path(__file__).resolve().parent.parent

    print(f"[REQUEST] {request.question}")

    try:
        result = answer_question(request.question, project_root, "default")

        return build_response(
            success=True,
            data=result,
        )

    except Exception as e:
        print(f"[ERROR] {str(e)}")

        return build_response(
            success=False,
            error=str(e),
        )
    
class WhatsAppRequest(BaseModel):
    message: str
    user: str | None = "default"


@app.post("/whatsapp")
def whatsapp(request: WhatsAppRequest):
    project_root = Path(__file__).resolve().parent.parent

    print(f"[WHATSAPP] user={request.user} message={request.message}")

    try:
        result = answer_question(request.message, project_root, request.user)

        reply_text = result.get("answer", "Geen antwoord beschikbaar.")

        return {
            "reply": reply_text,
            "meta": {
                "intent": result.get("intent"),
                "day": result.get("day_number"),
                "current_day": result.get("current_day"),
                "user": result.get("user"),
            },
        }

    except Exception as e:
        print(f"[WHATSAPP ERROR] {str(e)}")

        return {
            "reply": "Er ging iets mis bij het verwerken van je bericht.",
            "error": str(e),
        }
    
class WhatsAppRequest(BaseModel):
    message: str
    user: str | None = "default"

@app.post("/twilio/whatsapp")
def twilio_whatsapp(
    Body: str = Form(default=""),
    From: str = Form(default="unknown"),
):
    project_root = Path(__file__).resolve().parent.parent

    user = From.replace("whatsapp:", "")
    message = Body.strip()

    print(f"[TWILIO] from={user} body={message}")

    try:
        result = answer_question(message, project_root, user)
        reply = escape(result.get("answer", "Geen antwoord beschikbaar."))
    except Exception as e:
        print(f"[TWILIO ERROR] {e}")
        reply = escape("Er liep iets mis bij het verwerken van je bericht.")

    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>{reply}</Message>
</Response>"""

    return Response(content=xml_response, media_type="application/xml")