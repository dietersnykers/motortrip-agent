from pathlib import Path
import json
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


def resolve_day_from_text(day_text: str, current_day: int) -> int | None:
    cleaned = day_text.strip().lower()

    if cleaned == "vandaag":
        return current_day

    if cleaned == "morgen":
        return current_day + 1

    if cleaned.isdigit():
        return int(cleaned)

    return None


def parse_user_input(user_input: str):
    parts = user_input.strip().lower().split()

    if not parts:
        return None, None

    if user_input.strip().lower() == "stop":
        return "stop", None

    if user_input.strip().lower() == "dag":
        return "dag", None

    if len(parts) == 3 and parts[0] == "zet" and parts[1] == "dag" and parts[2].isdigit():
        return "zet_dag", int(parts[2])

    command = parts[0]

    if command not in ["briefing", "hotel", "highlights", "route"]:
        return None, None

    if len(parts) >= 2:
        return command, parts[1]

    return command, None


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

    print("Beschikbare commando's: briefing, hotel, highlights, route, dag, zet dag X, stop")
    print("Voorbeelden: 'hotel vandaag', 'briefing morgen', 'route 1', 'zet dag 2'")

    while True:
        current_day = get_current_day(settings_path)
        user_input = input(f"\n[actieve dag: {current_day}] Wat wil je weten? ").strip()

        command, raw_day_value = parse_user_input(user_input)

        if command == "stop":
            print("Tot later.")
            break

        if command == "dag":
            print(f"De actieve dag is momenteel dag {current_day}.")
            continue

        if command == "zet_dag":
            set_current_day(settings_path, raw_day_value)
            print(f"Actieve dag aangepast naar dag {raw_day_value}.")
            continue

        if command is None:
            print("Onbekend commando. Gebruik bijvoorbeeld: 'hotel vandaag', 'briefing morgen', 'route 1', 'zet dag 2'")
            continue

        if raw_day_value is None:
            extra_input = input("Voor welke dag? ").strip()
            day_number = resolve_day_from_text(extra_input, current_day)
        else:
            day_number = resolve_day_from_text(str(raw_day_value), current_day)

        if day_number is None:
            print("Ik begrijp de dag niet. Gebruik bijvoorbeeld: vandaag, morgen, 1, 2 ...")
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

        if command == "briefing":
            print(build_briefing(day_number, day_row, gpx_data, hotel_row, highlights))
        elif command == "hotel":
            print(build_hotel_text(hotel_row))
        elif command == "highlights":
            print(build_highlights_text(highlights))
        elif command == "route":
            print(build_route_text(day_number, day_row, gpx_data))


if __name__ == "__main__":
    main()