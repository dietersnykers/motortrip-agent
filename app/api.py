from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
import datetime

from app.agent_service import answer_question

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
        result = answer_question(request.question, project_root)

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