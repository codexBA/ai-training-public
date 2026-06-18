"""
BiH gradovi s geografskim koordinatama za Open-Meteo API.
"""

BIH_CITIES = {
    "sarajevo": {"lat": 43.8563, "lon": 18.4131, "display": "Sarajevo"},
    "banja luka": {"lat": 44.7722, "lon": 17.1910, "display": "Banja Luka"},
    "mostar": {"lat": 43.3438, "lon": 17.8078, "display": "Mostar"},
    "tuzla": {"lat": 44.5386, "lon": 18.6769, "display": "Tuzla"},
    "zenica": {"lat": 44.2014, "lon": 17.9078, "display": "Zenica"},
    "bihac": {"lat": 44.8167, "lon": 15.8708, "display": "Bihać"},
    "bijeljina": {"lat": 44.7569, "lon": 19.2169, "display": "Bijeljina"},
    "trebinje": {"lat": 42.7112, "lon": 18.3441, "display": "Trebinje"},
    "brcko": {"lat": 44.8728, "lon": 18.8083, "display": "Brčko"},
    "livno": {"lat": 43.8269, "lon": 17.0078, "display": "Livno"},
}


def normalize_city(name: str) -> str:
    """Normalizuje naziv grada za lookup."""
    return name.strip().lower().replace("ć", "c").replace("č", "c").replace("š", "s").replace("ž", "z")


def find_city(name: str) -> dict | None:
    """
    Pronalazi grad po nazivu (case-insensitive, dijakritici opciono).
    Vraća dict s lat, lon, display ili None.
    """
    key = normalize_city(name)
    if key in BIH_CITIES:
        return BIH_CITIES[key]
    # Pokušaj bez normalizacije dijakritika
    for k, v in BIH_CITIES.items():
        if k == name.strip().lower():
            return v
    return None


def list_cities() -> list[str]:
    """Vraća listu podržanih gradova za prikaz."""
    return [v["display"] for v in BIH_CITIES.values()]
