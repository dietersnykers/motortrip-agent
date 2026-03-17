from pathlib import Path
import json


def load_settings(settings_path: Path) -> dict:
    if not settings_path.exists():
        return {"current_day": 1}

    with open(settings_path, "r") as f:
        return json.load(f)


def save_settings(settings_path: Path, settings: dict) -> None:
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)


def get_current_day(settings_path: Path) -> int:
    settings = load_settings(settings_path)
    return settings.get("current_day", 1)


def set_current_day(settings_path: Path, day_number: int) -> None:
    settings = load_settings(settings_path)
    settings["current_day"] = day_number
    save_settings(settings_path, settings)