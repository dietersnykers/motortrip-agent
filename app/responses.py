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

def build_help_text() -> str:
    return (
        "Ik kan je helpen met info over de reis.\n\n"
        "Voorbeelden:\n"
        "- waar slapen we vandaag\n"
        "- geef briefing voor morgen\n"
        "- wat zijn de highlights vandaag\n"
        "- toon route voor dag 2\n"
        "- dag\n"
        "- zet dag 2"
    )


def build_unknown_question_text() -> str:
    return (
        "Die vraag snap ik nog niet helemaal.\n\n"
        "Probeer bijvoorbeeld:\n"
        "- waar slapen we vandaag\n"
        "- briefing morgen\n"
        "- highlights dag 2\n"
        "- zet dag 2"
    )


def build_missing_day_text(intent: str | None) -> str:
    if intent == "hotel":
        return "Voor welke dag wil je hotelinfo? Bijvoorbeeld: vandaag, morgen of dag 2."
    if intent == "briefing":
        return "Voor welke dag wil je een briefing? Bijvoorbeeld: vandaag, morgen of dag 2."
    if intent == "route":
        return "Voor welke dag wil je route-info? Bijvoorbeeld: vandaag, morgen of dag 2."
    if intent == "highlights":
        return "Voor welke dag wil je de highlights? Bijvoorbeeld: vandaag, morgen of dag 2."

    return "Voor welke dag wil je info? Bijvoorbeeld: vandaag, morgen of dag 2."


def build_short_hotel_text(hotel_row) -> str:
    if hotel_row is None:
        return "Ik vond geen hotelinfo voor die dag."

    return (
        f"🏨 {hotel_row['hotel_name']} — {hotel_row['city']}\n"
        f"📍 {hotel_row['address']}\n"
        f"🔗 {hotel_row['booking_url']}"
    )


def build_short_highlights_text(highlights: list) -> str:
    if not highlights:
        return "Nog geen highlights ingevoerd voor deze dag."

    lines = ["⭐ Highlights van die dag:"]
    for item in highlights[:3]:
        lines.append(f"- {item['name']}")

    return "\n".join(lines)


def build_short_route_text(day_number: int, day_row, gpx_data: dict) -> str:
    distance_km = gpx_data["distance_km"]

    title = f"Dag {day_number}"
    start_name = "Onbekende startplaats"
    end_name = "Onbekende eindplaats"

    if day_row is not None:
        title = day_row["title"]
        start_name = day_row["start_name"]
        end_name = day_row["end_name"]

    return (
        f"🛣️ {title}\n"
        f"Van {start_name} naar {end_name}\n"
        f"Afstand: ongeveer {distance_km} km"
    )


def build_short_briefing(day_number: int, day_row, gpx_data: dict, hotel_row, highlights: list) -> str:
    route_text = build_short_route_text(day_number, day_row, gpx_data)
    hotel_text = build_short_hotel_text(hotel_row)

    highlight_line = "Geen highlights ingevoerd."
    if highlights:
        highlight_line = f"⭐ Tip: {highlights[0]['name']}"

    return (
        f"{route_text}\n\n"
        f"{hotel_text}\n\n"
        f"{highlight_line}"
    )

def build_raw_facts_for_advice(day_number: int, day_row, gpx_data: dict, hotel_row, highlights: list) -> str:
    distance_km = gpx_data["distance_km"]

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

    hotel_info = "Geen hotelinformatie beschikbaar."
    if hotel_row is not None:
        hotel_info = (
            f"Hotel: {hotel_row['hotel_name']} in {hotel_row['city']}. "
            f"Check-in: {hotel_row['checkin_notes']}. "
            f"Parking: {hotel_row['parking_notes']}."
        )

    highlights_info = "Geen highlights beschikbaar."
    if highlights:
        highlight_lines = [f"- {item['name']}: {item['description']}" for item in highlights[:3]]
        highlights_info = "\n".join(highlight_lines)

    return (
        f"Dag: {title}\n"
        f"Start: {start_name}\n"
        f"Einde: {end_name}\n"
        f"Afstand: {distance_km} km\n"
        f"Type dag: {ride_style}\n"
        f"Route samenvatting: {region_summary}\n\n"
        f"{hotel_info}\n\n"
        f"Highlights:\n{highlights_info}"
    )


def build_short_advice_text(day_number: int, day_row, gpx_data: dict, hotel_row, highlights: list) -> str:
    distance_km = gpx_data["distance_km"]

    advice_lines = []

    if distance_km < 180:
        advice_lines.append("Vandaag is relatief ontspannen, dus neem gerust tijd voor een extra stop.")
    elif distance_km < 300:
        advice_lines.append("Vandaag is een mooie gemiddelde rijdag: ideaal om vlot te vertrekken maar onderweg nog te stoppen.")
    else:
        advice_lines.append("Vandaag is een stevigere rit, dus vertrek best op tijd en hou je stops een beetje strak.")

    if highlights:
        advice_lines.append(f"Probeer zeker even te stoppen bij {highlights[0]['name']}.")

    if hotel_row is not None and str(hotel_row.get("parking_notes", "")).strip():
        advice_lines.append(f"Denk bij aankomst aan de parking: {hotel_row['parking_notes']}")

    return "\n".join(advice_lines)

def build_raw_facts_for_hotel(hotel_row) -> str:
    if hotel_row is None:
        return "Geen hotelinformatie gevonden voor deze dag."

    return (
        f"Hotelnaam: {hotel_row['hotel_name']}\n"
        f"Stad: {hotel_row['city']}\n"
        f"Adres: {hotel_row['address']}\n"
        f"Boekingslink: {hotel_row['booking_url']}\n"
        f"Check-in: {hotel_row['checkin_notes']}\n"
        f"Parking: {hotel_row['parking_notes']}"
    )


def build_raw_facts_for_highlights(highlights: list) -> str:
    if not highlights:
        return "Nog geen highlights ingevoerd voor deze dag."

    lines = []
    for item in highlights[:3]:
        lines.append(f"- {item['name']}: {item['description']}")

    return "\n".join(lines)


def build_raw_facts_for_route(day_number: int, day_row, gpx_data: dict) -> str:
    distance_km = gpx_data["distance_km"]

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
        f"Titel: {title}\n"
        f"Start: {start_name}\n"
        f"Einde: {end_name}\n"
        f"Afstand: {distance_km} km\n"
        f"Type dag: {ride_style}\n"
        f"Samenvatting route: {region_summary}"
    )


def build_raw_facts_for_briefing(day_number: int, day_row, gpx_data: dict, hotel_row, highlights: list) -> str:
    route_facts = build_raw_facts_for_route(day_number, day_row, gpx_data)
    hotel_facts = build_raw_facts_for_hotel(hotel_row)
    highlights_facts = build_raw_facts_for_highlights(highlights)

    return (
        f"ROUTE\n{route_facts}\n\n"
        f"HOTEL\n{hotel_facts}\n\n"
        f"HIGHLIGHTS\n{highlights_facts}"
    )

def build_raw_facts_for_morning(day_number: int, day_row, gpx_data: dict, hotel_row, highlights: list) -> str:
    route_facts = build_raw_facts_for_route(day_number, day_row, gpx_data)
    hotel_facts = build_raw_facts_for_hotel(hotel_row)
    highlights_facts = build_raw_facts_for_highlights(highlights)
    advice_facts = build_raw_facts_for_advice(day_number, day_row, gpx_data, hotel_row, highlights)

    return (
        f"GOEDEMORGEN BRIEFING\n\n"
        f"ROUTE\n{route_facts}\n\n"
        f"HOTEL\n{hotel_facts}\n\n"
        f"HIGHLIGHTS\n{highlights_facts}\n\n"
        f"ADVIES\n{advice_facts}"
    )


def build_short_morning_text(day_number: int, day_row, gpx_data: dict, hotel_row, highlights: list) -> str:
    route_text = build_short_route_text(day_number, day_row, gpx_data)
    hotel_text = build_short_hotel_text(hotel_row)

    highlight_line = "Nog geen highlight ingevoerd."
    if highlights:
        highlight_line = f"Leuke stop vandaag: {highlights[0]['name']}"

    return (
        f"Goedemorgen.\n\n"
        f"{route_text}\n\n"
        f"{highlight_line}\n\n"
        f"{hotel_text}"
    )
def build_raw_facts_for_stops(day_number: int, day_row, gpx_data: dict, highlights: list, stop_type: str = "general") -> str:
    distance_km = gpx_data["distance_km"]

    title = f"Dag {day_number}"
    region_summary = "Geen extra routesamenvatting beschikbaar."

    if day_row is not None:
        title = day_row["title"]
        region_summary = day_row["region_summary"]

    highlight_lines = "Geen highlights beschikbaar."
    if highlights:
        lines = []
        for item in highlights[:5]:
            lines.append(f"- {item['name']} ({item['type']}): {item['description']}")
        highlight_lines = "\n".join(lines)

    return (
        f"Dag: {title}\n"
        f"Afstand: {distance_km} km\n"
        f"Type vraag: {stop_type}\n"
        f"Route samenvatting: {region_summary}\n\n"
        f"Beschikbare highlights:\n{highlight_lines}"
    )


def build_short_stops_text(highlights: list, stop_type: str = "general") -> str:
    if not highlights:
        return "Ik heb nog geen goede stopinfo voor deze dag."

    title = "Mogelijke stops:"
    if stop_type == "coffee":
        title = "Mogelijke koffiestops:"
    elif stop_type == "lunch":
        title = "Mogelijke lunchstops:"

    lines = [title]
    for item in highlights[:3]:
        lines.append(f"- {item['name']}")

    return "\n".join(lines)