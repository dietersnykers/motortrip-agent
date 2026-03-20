from pathlib import Path
from app.llm_parser import parse_with_llm, resolve_llm_day
from app.data_loader import load_csv, get_row_for_day, get_day_highlights
from app.gpx_utils import load_gpx_data
from app.settings import get_current_day, set_current_day
from app.conversation_state import get_user_context, set_user_context
from app.parser import detect_intent, extract_day_reference, extract_set_day_value
from app.responses import (
    build_hotel_text,
    build_highlights_text,
    build_route_text,
    build_briefing,
    build_help_text,
    build_unknown_question_text,
    build_missing_day_text,
    build_short_hotel_text,
    build_short_highlights_text,
    build_short_route_text,
    build_short_briefing,
)


def get_project_paths(project_root: Path) -> dict:
    return {
        "hotels_csv": project_root / "data" / "imports" / "hotels.csv",
        "highlights_csv": project_root / "data" / "imports" / "highlights.csv",
        "trip_days_csv": project_root / "data" / "imports" / "trip_days.csv",
        "settings_json": project_root / "data" / "imports" / "settings.json",
        "conversations_json": project_root / "data" / "imports" / "conversations.json",
    }


def load_all_data(project_root: Path) -> dict:
    paths = get_project_paths(project_root)

    return {
        "hotels_df": load_csv(paths["hotels_csv"]),
        "highlights_df": load_csv(paths["highlights_csv"]),
        "trip_days_df": load_csv(paths["trip_days_csv"]),
        "settings_path": paths["settings_json"],
        "conversations_path": paths["conversations_json"],
    }


def answer_question(question: str, project_root: Path, user: str = "default") -> dict:
    data = load_all_data(project_root)

    hotels_df = data["hotels_df"]
    highlights_df = data["highlights_df"]
    trip_days_df = data["trip_days_df"]
    settings_path = data["settings_path"]
    current_day = get_current_day(settings_path, user)
    conversations_path = data["conversations_path"]
    user_context = get_user_context(conversations_path, user)
    last_intent = user_context.get("last_intent")
    last_day_number = user_context.get("last_day_number")

    intent = detect_intent(question)
    llm_parsed = None

    normalized_question = question.strip().lower()

    follow_up_only_day = normalized_question in ["en morgen?", "morgen?", "en vandaag?", "vandaag?"]
    follow_up_switch_topic = normalized_question in ["en de highlights?", "en highlights?", "en het hotel?", "en de route?", "en briefing?"]

    if intent is None and follow_up_only_day and last_intent:
        intent = last_intent

    if intent is None and follow_up_switch_topic:
        if "highlight" in normalized_question:
            intent = "highlights"
        elif "hotel" in normalized_question:
            intent = "hotel"
        elif "route" in normalized_question:
            intent = "route"
        elif "briefing" in normalized_question:
            intent = "briefing"

    if intent is None:
        llm_parsed = parse_with_llm(question)
        if llm_parsed:
            intent = llm_parsed.get("intent")
            if intent == "unknown":
                intent = None

    if intent == "stop":
        return {
            "answer": "Gebruik 'stop' alleen in de terminalversie.",
            "intent": "stop",
            "day_number": None,
            "current_day": current_day,
            "user": user,
        }

    if intent == "help":
        return {
            "answer": build_help_text(),
            "intent": "help",
            "day_number": None,
            "current_day": current_day,
            "user": user,
        }

    if intent == "show_day":
        return {
            "answer": f"De actieve dag is momenteel dag {current_day}.",
            "intent": "show_day",
            "day_number": current_day,
            "current_day": current_day,
            "user": user,
        }

    if intent == "set_day":
        new_day = extract_set_day_value(question)

        if new_day is None and llm_parsed:
            new_day = llm_parsed.get("set_day_value")

        if new_day is None:
            return {
                "answer": "Gebruik bijvoorbeeld: zet dag 2",
                "intent": "set_day",
                "day_number": None,
                "current_day": current_day,
                "user": user,
            }

        set_current_day(settings_path, user, new_day)
        return {
            "answer": f"Actieve dag aangepast naar dag {new_day}.",
            "intent": "set_day",
            "day_number": new_day,
            "current_day": new_day,
            "user": user,
        }

    if intent is None:
        return {
            "answer": build_unknown_question_text(),
            "intent": None,
            "day_number": None,
            "current_day": current_day,
            "user": user,
        }

    day_number = extract_day_reference(question, current_day)

    if day_number is None and follow_up_only_day:
        if "morgen" in normalized_question:
            if last_day_number is not None:
                day_number = last_day_number + 1
            else:
                day_number = current_day + 1
        elif "vandaag" in normalized_question:
            day_number = current_day

    if day_number is None and llm_parsed:
        day_number = resolve_llm_day(llm_parsed, current_day)

    if day_number is None and last_day_number is not None and intent == last_intent:
        day_number = last_day_number

    if day_number is None and llm_parsed:
        day_number = resolve_llm_day(llm_parsed, current_day)

    if day_number is None:
        return {
            "answer": build_missing_day_text(intent),
            "intent": intent,
            "day_number": None,
            "current_day": current_day,
            "user": user,
        }

    gpx_path = project_root / "data" / "gpx" / f"day_{day_number}.gpx"

    if not gpx_path.exists():
        return {
            "answer": f"Geen GPX-bestand gevonden voor dag {day_number}.",
            "intent": intent,
            "day_number": day_number,
            "current_day": current_day,
            "user": user,
        }

    gpx_data = load_gpx_data(gpx_path)
    hotel_row = get_row_for_day(hotels_df, day_number)
    day_row = get_row_for_day(trip_days_df, day_number)
    highlights = get_day_highlights(highlights_df, day_number)

    if intent == "hotel":
        answer = build_short_hotel_text(hotel_row)
    elif intent == "highlights":
        answer = build_short_highlights_text(highlights)
    elif intent == "route":
        answer = build_short_route_text(day_number, day_row, gpx_data)
    elif intent == "briefing":
        answer = build_short_briefing(day_number, day_row, gpx_data, hotel_row, highlights)
    else:
        answer = "Ik heb nog geen antwoord voor die vraag."

    set_user_context(
        conversations_path=conversations_path,
        user=user,
        last_intent=intent,
        last_day_number=day_number,
        last_question=question,
    )    

    return {
        "answer": answer,
        "intent": intent,
        "day_number": day_number,
        "current_day": current_day,
        "source": "motortrip-agent-v1",
        "user": user,
    }