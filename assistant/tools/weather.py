"""Weather forecast from Open-Meteo (free, no API key)."""

import json
import urllib.parse
import urllib.request

from strands import tool


def _get(url: str, **params) -> dict:
    """GET an Open-Meteo URL with query parameters and return the JSON (10 second timeout)."""
    with urllib.request.urlopen(f"{url}?{urllib.parse.urlencode(params)}", timeout=10) as resp:
        return json.load(resp)


@tool
def get_weather(place: str, days: int = 3) -> dict:
    """Get the daily weather forecast for a place.

    Args:
        place: City name, with the state and country when you know them,
            e.g. "Ensenada" or "Valle de Guadalupe, Baja California, Mexico".
        days: Number of days to forecast, 1 to 7.
    """
    name, *hints = [part.strip().lower() for part in place.split(",")]
    found = _get("https://geocoding-api.open-meteo.com/v1/search", name=name, count=10)
    if not found.get("results"):
        return {"error": f"Place not found: {place}"}
    # Many places share a name (there are seven Valle de Guadalupes in Mexico):
    # prefer the one whose state, municipality or country matches the rest of what was asked.
    def matches(r: dict) -> int:
        """How many of the extra hints in the place (state, country) appear in this geocoder result."""
        where = " ".join(str(r.get(k, "")) for k in ("admin1", "admin2", "country")).lower()
        return sum(hint in where for hint in hints)

    loc = max(found["results"], key=matches)  # ties keep the geocoder's order (most relevant first)
    forecast = _get(
        "https://api.open-meteo.com/v1/forecast",
        latitude=loc["latitude"],
        longitude=loc["longitude"],
        daily="temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max,uv_index_max",
        timezone="auto",
        forecast_days=max(1, min(days, 7)),
    )
    return {"place": f'{loc["name"]}, {loc.get("admin1", "")}, {loc.get("country", "")}', **forecast["daily"]}


TOOLS = [get_weather]
