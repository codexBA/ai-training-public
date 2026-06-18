"""
Direktni Open-Meteo poziv — bez LLM, za debug i učenje API-ja.

Pokretanje:
    python cli/meteo_direct.py Sarajevo
    python cli/meteo_direct.py Mostar 5
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.weather import get_weather_forecast, list_supported_cities


def main():
    if len(sys.argv) < 2:
        gradovi = list_supported_cities()
        print("Upotreba: python cli/meteo_direct.py <grad> [dani]")
        print("Podrzani gradovi:", ", ".join(gradovi["gradovi"]))
        return

    city = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    print(f"Dohvatam prognozu za {city}, {days} dana...\n")
    rezultat = get_weather_forecast(city, days)
    print(json.dumps(rezultat, indent=2, ensure_ascii=False))

    if rezultat.get("iz_cachea"):
        print("\n(Napomena: podaci iz cache-a — ponovite za svjež API poziv nakon 5 min)")


if __name__ == "__main__":
    main()
