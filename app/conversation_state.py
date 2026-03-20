from pathlib import Path
import json


def load_conversations(conversations_path: Path) -> dict:
    if not conversations_path.exists():
        return {"users": {}}

    with open(conversations_path, "r") as f:
        return json.load(f)


def save_conversations(conversations_path: Path, data: dict) -> None:
    with open(conversations_path, "w") as f:
        json.dump(data, f, indent=2)


def get_user_context(conversations_path: Path, user: str) -> dict:
    data = load_conversations(conversations_path)
    return data.get("users", {}).get(user, {})


def set_user_context(
    conversations_path: Path,
    user: str,
    last_intent: str | None,
    last_day_number: int | None,
    last_question: str | None,
) -> None:
    data = load_conversations(conversations_path)

    if "users" not in data:
        data["users"] = {}

    data["users"][user] = {
        "last_intent": last_intent,
        "last_day_number": last_day_number,
        "last_question": last_question,
    }

    save_conversations(conversations_path, data)