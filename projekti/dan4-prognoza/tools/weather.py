"""
Open-Meteo vremenska prognoza s cache-om i timeout-om.
Besplatan API — bez registracije i API ključa.
"""

import json
import logging
import os
import time
from typing import Any

import httpx

from tools.cities import find_city, list_cities

logger = logging.getLogger("dan4-prognoza")

# In-memory cache: ključ -> (podaci, timestamp)
_cache: dict[str, tuple[dict, float]] = {}
CACHE_TTL = int(os.getenv("WEATHER_CACHE_TTL", "300"))
REQUEST_TIMEOUT = float(os.getenv("OPEN_METEO_TIMEOUT", "10.0"))

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _cache_key(city: str, days: int) -> str:
    return f"{city.lower()}:{days}"


def get_weather_forecast(city: str, days: int = 3) -> dict[str, Any]:
    """
    Dohvata vremensku prognozu za grad u BiH.

    Parametri:
        city - naziv grada (npr. Sarajevo)
        days - broj dana prognoze (1-7)

    Vraća:
        Dict s prognozom ili greškom
    """
    days = max(1, min(7, int(days)))
    ck = _cache_key(city, days)

    # KORAK 1: Provjera cache-a
    if ck in _cache:
        podaci, ts = _cache[ck]
        if time.time() - ts < CACHE_TTL:
            logger.info("cache HIT city=%s days=%s", city, days)
            podaci = dict(podaci)
            podaci["iz_cachea"] = True
            return podaci

    # KORAK 2: Lookup grada
    info = find_city(city)
    if not info:
        return {
            "greska": f"Grad '{city}' nije u bazi. Podržani: {', '.join(list_cities())}",
            "grad": city,
        }

    # KORAK 3: HTTP poziv Open-Meteo
    params = {
        "latitude": info["lat"],
        "longitude": info["lon"],
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": "Europe/Sarajevo",
        "forecast_days": days,
    }

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            raw = response.json()
    except httpx.TimeoutException:
        return {"greska": "Open-Meteo API timeout — pokušajte ponovo.", "grad": info["display"]}
    except httpx.HTTPError as exc:
        return {"greska": f"Open-Meteo greška: {exc}", "grad": info["display"]}

    # KORAK 4: Formatiranje odgovora
    daily = raw.get("daily", {})
    prognoza_dani = []
    datumi = daily.get("time", [])
    for i, datum in enumerate(datumi):
        prognoza_dani.append({
            "datum": datum,
            "temp_max_c": daily.get("temperature_2m_max", [None])[i],
            "temp_min_c": daily.get("temperature_2m_min", [None])[i],
            "padavine_mm": daily.get("precipitation_sum", [None])[i],
            "weather_code": daily.get("weathercode", [None])[i],
        })

    rezultat = {
        "grad": info["display"],
        "lat": info["lat"],
        "lon": info["lon"],
        "dani": days,
        "prognoza": prognoza_dani,
        "iz_cachea": False,
    }

    _cache[ck] = (rezultat, time.time())
    logger.info("cache MISS city=%s days=%s — spremljeno", city, days)
    return rezultat


def list_supported_cities() -> dict[str, Any]:
    """Vraća listu gradova koje aplikacija podržava."""
    return {"gradovi": list_cities(), "ukupno": len(list_cities())}


def execute_tool(name: str, arguments: str) -> str:
    """
    Izvršava alat po imenu — koristi se u function calling petlji.
    arguments je JSON string iz tool_call.
    """
    try:
        args = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError:
        return json.dumps({"greska": "Nevalidan JSON u argumentima alata"}, ensure_ascii=False)

    if name == "get_weather_forecast":
        city = args.get("city", "")
        days = args.get("days", 3)
        return json.dumps(get_weather_forecast(city, days), ensure_ascii=False)

    if name == "list_supported_cities":
        return json.dumps(list_supported_cities(), ensure_ascii=False)

    return json.dumps({"greska": f"Nepoznat alat: {name}"}, ensure_ascii=False)
