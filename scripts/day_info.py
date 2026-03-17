from pathlib import Path
import json
import re
import pandas as pd
import gpxpy


def load_csv(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


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


def load_gpx_data(gpx_path: Path) -> dict:
    with open(gpx_path, "r") as f:
        gpx = gpxpy.parse(f)

    distance = 0.0
    points = []

    for track in gpx.tracks:
        for segment in track.segments:
            distance += segment.length_3d()
            points.extend(segment.points)

    if not points:
        return {
            "distance_km": 0.0,
            "point_count": 0,
            "start_lat": None,
            "start_lon": None,
            "end_lat": None,
            "end_lon": None,
        }

    start = points[0]
    end = points[-1]

    return {
        "distance_km": round(distance / 1000, 1),
        "point_count": len(points),
        "start_lat": start.latitude,
        "start_lon": start.longitude,
        "end_lat": end.latitude,
        "end_lon": end.longitude,
    }


def get_row_for_day(df: pd.DataFrame, day_number: int):
    row = df[df["day_number"] == day_number]
    if row.empty:
        return None
    return row.iloc[0]


def get_day_highlights(highlights_df: pd.DataFrame, day_number: int) -> list:
    day_rows = highlights_df[highlights_df["day_number"] == day_number]
    highlights = []

    for _, row in day_rows.iterrows():
        highlights.append(
            {
                "name": row["name"],
                "type": row["type"],
                "description": row["description"],
            }
        )

    return highlights


def estimate_route_character(distance_km: float) -> str:
    if distance_km < 150:
        return "eerder een korte en ontspannen rijdag"
    if distance_km < 275:
        return "een mooie gemiddelde rijdag met genoeg tijd voor stops"
    if distance_km < 400:
        return "een stevigere rijdag waarbij je best vlot doorrijdt"
    return "een lange rijdag waarvoor je best op tijd vertrekt"


def build_hotel_text(hotel_row) -> str:
    if hotel_row is None:
        return "Geen hotelinformatie gevonden voor deze dag."

    return (
        f"Vanavond slapen we in {hotel_row['hotel_name']} in {hotel_row['city']}.\n"
        f"Adres: {hotel_row['address']}\n"
        f"Boekingslink: {hotel_row['booking_url']}\n"
        f"Praktisch: {hotel_row['checkin_notes']} | Parking: {hotel_row['parking_notes']}"
    )


def build_highlights_text(highlights: list) -> str:
    if not highlights:
        return "Nog geen highlights ingevoerd voor deze dag."

    lines = []
    for item in highlights[:3]:
        lines.append(f"- {item['name']}: {item['description']}")

    return "\n".join(lines)


def build_route_text(day_number: int, day_row, gpx_data: dict) -> str:
    distance_km = gpx_data["distance_km"]
    route_character = estimate_route_character(distance_km)

    title = f"Dag {day_number}"
    start_name = "Onbekende startplaats"
    end_name = "Onbekende eindplaats"
    region_summary = "Geen extra routesamenvatting beschikbaar."
    ride_style = "Rijdag"

    if day_row is not None:
        title = day_row["title"]
        start_name = day_row["start_name"]
        end_name = day_row["end_name"]
        region_summary = day_row["region_summary"]
        ride_style = day_row["ride_style"]

    return (
        f"Dag {day_number} — {title}\n\n"
        f"Start: {start_name}\n"
        f"Einde: {end_name}\n\n"
        f"Afstand: ongeveer {distance_km} km\n"
        f"Type dag: {ride_style}\n"
        f"Routekarakter: {route_character}\n\n"
        f"Route\n{region_summary}"
    )


def build_briefing(day_number: int, day_row, gpx_data: dict, hotel_row, highlights: list) -> str:
    route_text = build_route_text(day_number, day_row, gpx_data)
    hotel_text = build_hotel_text(hotel_row)
    highlights_text = build_highlights_text(highlights)

    return (
        f"{route_text}\n\n"
        f"Hotel\n{hotel_text}\n\n"
        f"Highlights\n{highlights_text}\n\n"
        f"Kort samengevat:\n"
        f"Een route om van te genieten, met genoeg reden om onderweg af en toe af te stappen voor koffie, foto's en uitzicht."
    )


def extract_day_reference(user_input: str, current_day: int) -> int | None:
    text = user_input.lower()

    if "vandaag" in text:
        return current_day

    if "morgen" in text:
        return current_day + 1

    match = re.search(r"dag\s+(\d+)", text)
    if match:
        return int(match.group(1))

    if text.strip().isdigit():
        return int(text.strip())

    standalone_number = re.search(r"\b(\d+)\b", text)
    if standalone_number:
        return int(standalone_number.group(1))

    return None


def detect_intent(user_input: str) -> str | None:
    text = user_input.lower().strip()

    if text in ["stop", "quit", "exit"]:
        return "stop"

    if text == "dag":
        return "show_day"

    if text.startswith("zet dag"):
        return "set_day"

    if any(word in text for word in ["hotel", "slapen", "overnachten"]):
        return "hotel"

    if any(word in text for word in ["highlight", "highlights", "stop", "fotoplek", "foto", "beziens", "mooi onderweg"]):
        return "highlights"

    if any(word in text for word in ["route", "afstand", "rijden", "traject"]):
        return "route"

    if any(word in text for word in ["briefing", "samenvatting", "vertel over", "wat mogen we verwachten"]):
        return "briefing"

    return None


def extract_set_day_value(user_input: str) -> int | None:
    match = re.search(r"zet\s+dag\s+(\d+)", user_input.lower())
    if match:
        return int(match.group(1))
    return None


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