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


def ask_for_day_if_needed(current_day: int) -> int | None:
    extra_input = input("Voor welke dag? ").strip()
    return extract_day_reference(extra_input, current_day)


def main():
    project_root = Path(__file__).resolve().parent.parent

    hotels_csv_path = project_root / "data" / "sample" / "hotels_example.csv"
    highlights_csv_path = project_root / "data" / "sample" / "highlights_example.csv"
    trip_days_csv_path = project_root / "data" / "sample" / "trip_days_example.csv"
    settings_path = project_root / "data" / "sample" / "settings.json"

    if not hotels_csv_path.exists():
        print(f"Geen hotelbestand gevonden: {hotels_csv_path}")
        return

    if not highlights_csv_path.exists():
        print(f"Geen highlights-bestand gevonden: {highlights_csv_path}")
        return

    if not trip_days_csv_path.exists():
        print(f"Geen trip_days-bestand gevonden: {trip_days_csv_path}")
        return

    hotels_df = load_csv(hotels_csv_path)
    highlights_df = load_csv(highlights_csv_path)
    trip_days_df = load_csv(trip_days_csv_path)

    print("Je kan nu vrijer typen, bijvoorbeeld:")
    print("- waar slapen we vandaag")
    print("- geef briefing voor morgen")
    print("- wat zijn de highlights van dag 1")
    print("- toon route voor vandaag")
    print("- dag")
    print("- zet dag 2")
    print("- stop")

    while True:
        current_day = get_current_day(settings_path)
        user_input = input(f"\n[actieve dag: {current_day}] Vraag: ").strip()

        intent = detect_intent(user_input)

        if intent == "stop":
            print("Tot later.")
            break

        if intent == "show_day":
            print(f"De actieve dag is momenteel dag {current_day}.")
            continue

        if intent == "set_day":
            new_day = extract_set_day_value(user_input)
            if new_day is None:
                print("Gebruik bijvoorbeeld: zet dag 2")
                continue

            set_current_day(settings_path, new_day)
            print(f"Actieve dag aangepast naar dag {new_day}.")
            continue

        if intent is None:
            print("Ik snap de vraag nog niet goed. Probeer iets zoals 'waar slapen we vandaag' of 'geef briefing voor dag 2'.")
            continue

        day_number = extract_day_reference(user_input, current_day)

        if day_number is None:
            day_number = ask_for_day_if_needed(current_day)

        if day_number is None:
            print("Ik begrijp niet voor welke dag je info wil. Gebruik bijvoorbeeld: vandaag, morgen, dag 2 ...")
            continue

        gpx_path = project_root / "data" / "gpx" / f"day_{day_number}.gpx"

        if not gpx_path.exists():
            print(f"Geen GPX-bestand gevonden voor dag {day_number}: {gpx_path}")
            continue

        gpx_data = load_gpx_data(gpx_path)
        hotel_row = get_row_for_day(hotels_df, day_number)
        day_row = get_row_for_day(trip_days_df, day_number)
        highlights = get_day_highlights(highlights_df, day_number)

        print()

        if intent == "hotel":
            print(build_hotel_text(hotel_row))
        elif intent == "highlights":
            print(build_highlights_text(highlights))
        elif intent == "route":
            print(build_route_text(day_number, day_row, gpx_data))
        elif intent == "briefing":
            print(build_briefing(day_number, day_row, gpx_data, hotel_row, highlights))


if __name__ == "__main__":
    main()