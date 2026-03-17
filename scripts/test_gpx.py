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

print(f"GPX bestand: {gpx_file}")
print(f"Aantal punten: {len(points)}")
print(f"Totale afstand: {distance / 1000:.1f} km")

if points:
    start = points[0]
    end = points[-1]

    print("\nStart:")
    print(f"Lat: {start.latitude}, Lon: {start.longitude}")

    print("\nEinde:")
    print(f"Lat: {end.latitude}, Lon: {end.longitude}")