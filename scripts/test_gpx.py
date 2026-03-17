from pathlib import Path
import gpxpy

# bepaal project root
project_root = Path(__file__).resolve().parent.parent

gpx_file = project_root / "data" / "gpx" / "day_1.gpx"

print(f"GPX bestand: {gpx_file}")

with open(gpx_file, "r") as f:
    gpx = gpxpy.parse(f)

points = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append(point)

print(f"Aantal punten: {len(points)}")

if len(points) > 0:
    start = points[0]
    end = points[-1]

    print("\nStart:")
    print(f"Lat: {start.latitude}, Lon: {start.longitude}")

    print("\nEinde:")
    print(f"Lat: {end.latitude}, Lon: {end.longitude}")