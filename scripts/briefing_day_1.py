from pathlib import Path
import gpxpy

project_root = Path(__file__).resolve().parent.parent
gpx_file = project_root / "data" / "gpx" / "day_1.gpx"

with open(gpx_file, "r") as f:
    gpx = gpxpy.parse(f)

distance = 0.0
points = []

for track in gpx.tracks:
    for segment in track.segments:
        distance += segment.length_3d()
        points.extend(segment.points)

distance_km = round(distance / 1000, 1)

# Voorlopig vullen we start/einde nog handmatig in
start_name = "Hasselt"
end_name = "Moezelregio bij Cochem"

briefing = f"""
Dag 1 brengt ons van {start_name} naar {end_name}.
De rit is ongeveer {distance_km} km lang en vormt een mooie openingsdag van de reis.

Verwacht een rustige opbouw vanuit Limburg, daarna meer glooiende en bochtige trajecten richting de Ardennen en Duitsland.
Het slot richting de Moezel is meteen een hoogtepunt, met mooie vergezichten, wijngaarden en typische dorpjes langs de rivier.

Kort samengevat: een ontspannen maar gevarieerde eerste rijdag, ideaal om in het ritme van de trip te komen.
""".strip()

print(briefing)