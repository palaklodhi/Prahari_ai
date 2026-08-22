"""Geospatial Crime Pattern Intelligence.

Aggregates geolocated incidents into hotspots using a lightweight grid-based
spatial clustering (no scikit-geo deps), scores each hotspot, and emits patrol
prioritisation + inter-district intelligence-sharing recommendations plus a
GeoJSON layer for the command-centre map.
"""
from __future__ import annotations

import math
from collections import defaultdict

# grid cell size in degrees (~5.5 km at Indian latitudes)
CELL = 0.05


def _cell_key(lat: float, lon: float):
    return (round(lat / CELL), round(lon / CELL))


def compute_hotspots(incidents: list) -> dict:
    cells = defaultdict(list)
    for inc in incidents:
        cells[_cell_key(inc.lat, inc.lon)].append(inc)

    hotspots = []
    for (cy, cx), members in cells.items():
        if len(members) < 2:
            continue
        lat = sum(m.lat for m in members) / len(members)
        lon = sum(m.lon for m in members) / len(members)
        loss = sum(m.amount_loss for m in members)
        severity = sum(m.severity for m in members) / len(members)
        by_cat = defaultdict(int)
        for m in members:
            by_cat[m.category] += 1
        dominant = max(by_cat.items(), key=lambda kv: kv[1])[0]
        city = max(set(m.city for m in members), key=lambda c: sum(1 for m in members if m.city == c))
        state = members[0].state

        intensity = min(1.0, 0.12 * len(members) + min(0.4, loss / 20_000_000) + 0.08 * severity)
        priority = "critical" if intensity >= 0.75 else "high" if intensity >= 0.5 else "watch"

        hotspots.append({
            "id": f"HS-{cy}-{cx}",
            "lat": round(lat, 4), "lon": round(lon, 4),
            "city": city, "state": state,
            "incident_count": len(members),
            "total_loss": round(loss, 2),
            "avg_severity": round(severity, 2),
            "dominant_category": dominant,
            "category_breakdown": dict(by_cat),
            "intensity": round(intensity, 3),
            "priority": priority,
            "recommendation": _patrol_reco(priority, dominant, len(members)),
        })

    hotspots.sort(key=lambda h: h["intensity"], reverse=True)

    # state-level rollup for inter-district sharing
    state_roll = defaultdict(lambda: {"incidents": 0, "loss": 0.0})
    for inc in incidents:
        state_roll[inc.state]["incidents"] += 1
        state_roll[inc.state]["loss"] += inc.amount_loss

    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [h["lon"], h["lat"]]},
            "properties": h,
        } for h in hotspots],
    }

    return {
        "hotspots": hotspots,
        "geojson": geojson,
        "state_rollup": [{"state": k, **v, "loss": round(v["loss"], 2)}
                         for k, v in sorted(state_roll.items(), key=lambda kv: kv[1]["loss"], reverse=True)],
        "summary": {
            "total_incidents": len(incidents),
            "hotspots": len(hotspots),
            "critical_hotspots": sum(1 for h in hotspots if h["priority"] == "critical"),
            "total_loss": round(sum(i.amount_loss for i in incidents), 2),
        },
    }


def _patrol_reco(priority: str, category: str, count: int) -> str:
    cat = category.replace("_", " ")
    if priority == "critical":
        return (f"Deploy dedicated cyber-patrol unit; {count} clustered {cat} incidents. "
                f"Coordinate with adjacent districts and freeze linked mule accounts.")
    if priority == "high":
        return f"Increase patrol frequency and run awareness drive targeting {cat}."
    return f"Monitor emerging {cat} cluster; brief beat officers."
