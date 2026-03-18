from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

from app.agent_service import answer_question

app = FastAPI(title="Motortrip Agent API")


class AskRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "Motortrip Agent API draait"}


@app.post("/ask")
def ask(request: AskRequest):
    project_root = Path(__file__).resolve().parent.parent
    result = answer_question(request.question, project_root)
    return result