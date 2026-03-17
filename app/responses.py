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