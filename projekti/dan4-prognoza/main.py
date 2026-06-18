"""
Dan 4: Function Calling — AI koji koristi alate (Open-Meteo prognoza)
Pokretanje: uvicorn main:app --reload --port 8004
"""

import json
import logging
import os
import time
from typing import Any, List

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from pydantic import BaseModel

from tools.cities import list_cities
from tools.weather import execute_tool, get_weather_forecast, list_supported_cities

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dan4-prognoza")

app = FastAPI(title="Dan 4 — Prognoza (Function Calling)", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

MAX_TOOL_ITERATIONS = 3

DEFAULT_SYSTEM = """Ti si asistent za vremensku prognozu u Bosni i Hercegovini.
Koristi alate get_weather_forecast i list_supported_cities kada korisnik pita o vremenu.
Odgovaraj na bosanskom jeziku, jasno i sa konkretnim temperaturama iz alata.
Ako grad nije podržan, predloži list_supported_cities."""

# KORAK 1: Definicija alata (JSON schema) — model čita opis da zna KADA koristiti alat
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": (
                "Dohvata vremensku prognozu za grad u BiH. "
                "Koristi kada korisnik pita o temperaturi, kiši, vremenu, prognozi."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Naziv grada npr. Sarajevo, Mostar, Banja Luka",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Broj dana prognoze (1-7)",
                        "default": 3,
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_supported_cities",
            "description": "Vraća listu gradova za koje postoji prognoza. Koristi ako korisnik pita koje gradove podržavate.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def get_llm_client() -> tuple[AsyncOpenAI, str]:
    """Prioritet: DeepSeek API → Ollama lokalno."""
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    if deepseek_key and deepseek_key.startswith("sk-"):
        return AsyncOpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com"), "deepseek-chat"

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        httpx.get(f"{ollama_url}/api/tags", timeout=2.0)
        model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
        return AsyncOpenAI(api_key="ollama", base_url=f"{ollama_url}/v1"), model
    except Exception:
        raise RuntimeError(
            "Ni DeepSeek API ni Ollama nisu dostupni! Dodajte DEEPSEEK_API_KEY u .env."
        )


class ToolTraceEntry(BaseModel):
    korak: int
    alat: str
    argumenti: dict
    rezultat: Any
    trajanje_ms: int


class AskRequest(BaseModel):
    pitanje: str
    tool_choice: str = "auto"


class AskResponse(BaseModel):
    pitanje: str
    odgovor: str
    model: str
    tool_trace: List[ToolTraceEntry]
    iteracije: int
    trajanje_ms: int


async def run_tool_loop(
    klijent: AsyncOpenAI,
    model: str,
    messages: list,
    tool_choice: str = "auto",
) -> tuple[str, list[ToolTraceEntry], int]:
    """
    Function calling petlja — max MAX_TOOL_ITERATIONS iteracija.
    AI ne izvršava alate; mi izvršavamo i vraćamo rezultat.
    """
    trace: list[ToolTraceEntry] = []
    current_messages = list(messages)

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = await klijent.chat.completions.create(
            model=model,
            messages=current_messages,
            tools=TOOLS,
            tool_choice=tool_choice if iteration == 0 else "auto",
            temperature=0.3,
            max_tokens=500,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content or "", trace, iteration + 1

        # Dodaj assistant poruku s tool_calls
        current_messages.append(msg.model_dump(exclude_none=True))

        for tc in msg.tool_calls:
            pocetak = time.monotonic()
            fn_name = tc.function.name
            fn_args = tc.function.arguments or "{}"
            try:
                args_dict = json.loads(fn_args)
            except json.JSONDecodeError:
                args_dict = {"raw": fn_args}

            result_str = execute_tool(fn_name, fn_args)
            trajanje = int((time.monotonic() - pocetak) * 1000)

            trace.append(
                ToolTraceEntry(
                    korak=len(trace) + 1,
                    alat=fn_name,
                    argumenti=args_dict,
                    rezultat=json.loads(result_str),
                    trajanje_ms=trajanje,
                )
            )
            logger.info("tool_call %s args=%s ms=%s", fn_name, fn_args, trajanje)

            current_messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_str,
            })

    return "Ne mogu dovršiti zahtjev — previše koraka alata.", trace, MAX_TOOL_ITERATIONS


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/api/tools")
async def api_tools():
    """Lista definisanih alata za function calling."""
    return {"alati": TOOLS}


@app.get("/api/cities")
async def api_cities():
    return list_supported_cities()


@app.get("/api/weather/{city}")
async def api_weather_direct(city: str, days: int = 3):
    """Direktna prognoza bez AI — za test Open-Meteo integracije."""
    rezultat = get_weather_forecast(city, days)
    if "greska" in rezultat:
        raise HTTPException(status_code=404, detail=rezultat["greska"])
    return rezultat


@app.post("/api/ask", response_model=AskResponse)
async def ask(zahtjev: AskRequest):
    """
    Stateless pitanje — šalje samo system + user poruku (nema historije).
    Pokreće function calling petlju.
    """
    klijent, model = get_llm_client()
    pocetak = time.monotonic()

    messages = [
        {"role": "system", "content": DEFAULT_SYSTEM},
        {"role": "user", "content": zahtjev.pitanje},
    ]

    odgovor, trace, iteracije = await run_tool_loop(
        klijent, model, messages, zahtjev.tool_choice
    )
    trajanje = int((time.monotonic() - pocetak) * 1000)

    return AskResponse(
        pitanje=zahtjev.pitanje,
        odgovor=odgovor,
        model=model,
        tool_trace=trace,
        iteracije=iteracije,
        trajanje_ms=trajanje,
    )
