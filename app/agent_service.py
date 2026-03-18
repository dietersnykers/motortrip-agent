from pathlib import Path

from app.data_loader import load_csv, get_row_for_day, get_day_highlights
from app.gpx_utils import load_gpx_data
from app.settings import get_current_day, set_current_day
from app.parser import detect_intent, extract_day_reference, extract_set_day_value
from app.responses import (
    build_hotel_text,
    build_highlights_text,
    build_route_text,
    build_briefing,
)


def get_project_paths(project_root: Path) -> dict:
    return {
        "hotels_csv": project_root / "data" / "sample" / "hotels_example.csv",
        "highlights_csv": project_root / "data" / "sample" / "highlights_example.csv",
        "trip_days_csv": project_root / "data" / "sample" / "trip_days_example.csv",
        "settings_json": project_root / "data" / "sample" / "settings.json",
    }


def load_all_data(project_root: Path) -> dict:
    paths = get_project_paths(project_root)

    return {
        "hotels_df": load_csv(paths["hotels_csv"]),
        "highlights_df": load_csv(paths["highlights_csv"]),
        "trip_days_df": load_csv(paths["trip_days_csv"]),
        "settings_path": paths["settings_json"],
    }


def answer_question(question: str, project_root: Path) -> dict:
    data = load_all_data(project_root)

    hotels_df = data["hotels_df"]
    highlights_df = data["highlights_df"]
    trip_days_df = data["trip_days_df"]
    settings_path = data["settings_path"]

    current_day = get_current_day(settings_path)
    intent = detect_intent(question)

    if intent == "stop":
        return {"answer": "Gebruik 'stop' alleen in de terminalversie."}

    if intent == "show_day":
        return {"answer": f"De actieve dag is momenteel dag {current_day}."}

    if intent == "set_day":
        new_day = extract_set_day_value(question)
        if new_day is None:
            return {"answer": "Gebruik bijvoorbeeld: zet dag 2"}

        set_current_day(settings_path, new_day)
        return {"answer": f"Actieve dag aangepast naar dag {new_day}."}

    if intent is None:
        return {
            "answer": "Ik snap de vraag nog niet goed. Probeer iets zoals 'waar slapen we vandaag' of 'geef briefing voor dag 2'."
        }

    day_number = extract_day_reference(question, current_day)

    if day_number is None:
        return {
            "answer": "Ik begrijp niet voor welke dag je info wil. Gebruik bijvoorbeeld: vandaag, morgen, dag 2 ..."
        }

    gpx_path = project_root / "data" / "gpx" / f"day_{day_number}.gpx"

    if not gpx_path.exists():
        return {"answer": f"Geen GPX-bestand gevonden voor dag {day_number}."}

    gpx_data = load_gpx_data(gpx_path)
    hotel_row = get_row_for_day(hotels_df, day_number)
    day_row = get_row_for_day(trip_days_df, day_number)
    highlights = get_day_highlights(highlights_df, day_number)

    if intent == "hotel":
        answer = build_hotel_text(hotel_row)
    elif intent == "highlights":
        answer = build_highlights_text(highlights)
    elif intent == "route":
        answer = build_route_text(day_number, day_row, gpx_data)
    elif intent == "briefing":
        answer = build_briefing(day_number, day_row, gpx_data, hotel_row, highlights)
    else:
        answer = "Nog geen antwoord beschikbaar voor deze vraag."

    return {
        "answer": answer,
        "intent": intent,
        "day_number": day_number,
        "current_day": current_day,
    }