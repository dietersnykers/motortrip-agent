from pathlib import Path
import json


def load_settings(settings_path: Path) -> dict:
    if not settings_path.exists():
        return {"users": {}}

    with open(settings_path, "r") as f:
        return json.load(f)


def save_settings(settings_path: Path, settings: dict) -> None:
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)


def get_current_day(settings_path: Path, user: str) -> int:
    settings = load_settings(settings_path)
    users = settings.get("users", {})

    return users.get(user, 1)  # default dag 1


def set_current_day(settings_path: Path, user: str, day_number: int) -> None:
    settings = load_settings(settings_path)

    if "users" not in settings:
        settings["users"] = {}

    settings["users"][user] = day_number

    save_settings(settings_path, settings)