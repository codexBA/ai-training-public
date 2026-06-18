# Function Calling Prognoza — Dan 4

## Svrha

AI asistent koji **koristi alate** (function calling) za dohvat stvarne vremenske prognoze preko **Open-Meteo** API-ja. Demonstrira tool use flow, JSON schema alata, cache i timeout.

## Pedagoški cilj

- Razumjeti da AI ne izvršava funkcije — samo vraća `tool_calls`
- Definisati alate s JSON schema (name, description, parameters)
- Implementirati petlju: LLM → tool call → izvršenje → rezultat → finalni odgovor
- Integrirati besplatan vanjski API (Open-Meteo) s cache-om
- **Stateless** `/api/ask` — bez multi-turn chat historije (kao mini-adresar)

## Dva klijenta

| Klijent | Lokacija | Namjena |
|---------|----------|---------|
| **Web** | port **8004** | Ask UI, tool trace panel, direktni Meteo test |
| **CLI Agent** | `cli/weather_agent.py` | Chat s `[TOOL CALL]` u terminalu |
| **CLI Direct** | `cli/meteo_direct.py` | Open-Meteo bez AI |

Vodič: [uputstvo.html](uputstvo.html) (detaljno) · [docs/dan4.html](../../docs/dan4.html) (kurikulum)

## Quick Start

```powershell
cd projekti\dan4-prognoza
copy .env.example .env
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```

Browser: **http://localhost:8004**

## CLI

```powershell
python cli/meteo_direct.py Sarajevo 3
python cli/weather_agent.py
```

## API

| Endpoint | Opis |
|----------|------|
| `POST /api/ask` | Stateless pitanje + function calling loop + tool_trace |
| `GET /api/weather/{city}` | Direktna prognoza (bez AI) |
| `GET /api/tools` | Definicija alata |
| `GET /api/cities` | Lista gradova BiH |

## Alati

1. `get_weather_forecast(city, days)` — Open-Meteo
2. `list_supported_cities()` — Sarajevo, Mostar, Banja Luka, ...

## Testiranje

- Web: "Kakva je prognoza za Tuzlu?" → tool_trace s get_weather_forecast
- Ponoviti isto pitanje → `iz_cachea: true` u trace rezultatu
- `python cli/meteo_direct.py Mostar` — JSON bez LLM

## Vježba prije/poslije

- **[mini-adresar](../mini-adresar/)** — isti function calling pattern i stateless `/api/ask`, ali s lokalnim sim-API-jem (JSON adresar); dobar uvod bez interneta

---

Autor: **Erkan Islamovic** | AI Trening
