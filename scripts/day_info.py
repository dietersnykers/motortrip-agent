from pathlib import Path
import pandas as pd
import gpxpy


def load_hotels(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def load_gpx_distance(gpx_path: Path) -> float:
    with open(gpx_path, "r") as f:
        gpx = gpxpy.parse(f)

    distance = 0.0

    for track in gpx.tracks:
        for segment in track.segments:
            distance += segment.length_3d()

    return round(distance / 1000, 1)


def get_day_hotel(df: pd.DataFrame, day_number: int):
    hotel = df[df["day_number"] == day_number]

    if hotel.empty:
        return None

    return hotel.iloc[0]


def build_briefing(day_number: int, distance_km: float, hotel_row) -> str:
    hotel_text = "Geen hotelinformatie gevonden."
    if hotel_row is not None:
        hotel_text = (
            f"Vanavond slapen we in {hotel_row['hotel_name']} in {hotel_row['city']}.\n"
            f"Adres: {hotel_row['address']}\n"
            f"Boekingslink: {hotel_row['booking_url']}"
        )

    briefing = f"""
Dag {day_number}

Vandaag rijden we ongeveer {distance_km} km.
Dit is een mooie rijdag met een mix van verbindingsstukken en leuke trajecten onderweg.

{hotel_text}

Kort samengevat: zorg dat je ontspannen vertrekt, geniet van de route, en hou onderweg tijd voor een koffiestop en een paar foto’s.
""".strip()

    return briefing


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "sample" / "hotels_example.csv"

    day_number = int(input("Welke dag wil je bekijken? "))

    gpx_path = project_root / "data" / "gpx" / f"day_{day_number}.gpx"

    if not gpx_path.exists():
        print(f"Geen GPX-bestand gevonden voor dag {day_number}: {gpx_path}")
        return

    if not csv_path.exists():
        print(f"Geen hotelbestand gevonden: {csv_path}")
        return

    hotels_df = load_hotels(csv_path)
    distance_km = load_gpx_distance(gpx_path)
    hotel_row = get_day_hotel(hotels_df, day_number)

    briefing = build_briefing(day_number, distance_km, hotel_row)
    print("\n" + briefing)


if __name__ == "__main__":
    main()