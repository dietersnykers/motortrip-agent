from pathlib import Path
import gpxpy


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