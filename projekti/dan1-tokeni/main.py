"""
Dan 1: Token vizualizator i Temperature playground
Svrha: Demonstrira tokenizaciju, temperaturu i osnove API poziva

Pokretanje:
    uvicorn main:app --reload --port 8001
    ILI: docker-compose up
"""

# KORAK 1: Uvozimo potrebne biblioteke
# fastapi = Python web framework za kreiranje API endpointa
from fastapi import FastAPI
# StaticFiles = servisira HTML/CSS/JS fajlove
from fastapi.staticfiles import StaticFiles
# FileResponse = vraća fajl kao HTTP odgovor
from fastapi.responses import FileResponse
# BaseModel = Pydantic klasa za validaciju request podataka
from pydantic import BaseModel
# List = Python typing za type hints
from typing import List
# asyncio = biblioteka za asinhrono programiranje (paralelni zahtjevi)
import asyncio
# time = za mjerenje trajanja API poziva
import time
# os = za čitanje environment varijabli
import os
# load_dotenv = čita .env fajl i postavlja environment varijable
from dotenv import load_dotenv
# OpenAI SDK = radi i s DeepSeek i Ollama API-jem (OpenAI-kompatibilan)
from openai import AsyncOpenAI

# KORAK 2: Učitavamo konfiguraciju iz .env fajla
# .env fajl NIKAD ne ide u git repo (u .gitignore)
load_dotenv()

# KORAK 3: Inicijalizacija FastAPI aplikacije
app = FastAPI(
    title="Dan 1 — Token Vizualizator",
    description="API za demonstraciju tokenizacije i temperature",
    version="1.0.0"
)

# KORAK 4: Servisiramo statičke fajlove (HTML, CSS, JS)
# mount() = "prikvači" folder na URL putanju
app.mount("/static", StaticFiles(directory="static"), name="static")


# KORAK 5: Definišemo helper funkciju za LLM klijent s fallbackom
def get_llm_client():
    """
    Vraća LLM klijent prema dostupnosti.
    Prioritet: DeepSeek API → Ollama lokalno

    Ova funkcija automatski prebacuje na lokalni model
    ako cloud API nije dostupan ili API key nije postavljen.
    """
    # httpx = HTTP klijent za provjeru dostupnosti Ollama servera
    import httpx

    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")

    # Pokušaj 1: DeepSeek API (cloud, bolji kvalitet)
    if deepseek_key and deepseek_key.startswith("sk-"):
        return AsyncOpenAI(
            api_key=deepseek_key,
            base_url="https://api.deepseek.com"
        ), "deepseek-chat"

    # Pokušaj 2: Ollama lokalno (fallback)
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        httpx.get(f"{ollama_url}/api/tags", timeout=2.0)
        model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
        return AsyncOpenAI(
            api_key="ollama",
            base_url=f"{ollama_url}/v1"
        ), model
    except Exception:
        raise RuntimeError(
            "Ni DeepSeek API ni Ollama nisu dostupni!\n"
            "Rješenje A: Dodajte DEEPSEEK_API_KEY u .env fajl\n"
            "Rješenje B: Pokrenite Ollama: docker-compose up ollama"
        )


# KORAK 6: Definišemo Pydantic modele za request/response validaciju
# Pydantic automatski validira tipove i vraća grešku ako nešto ne odgovara
class TemperatureRequest(BaseModel):
    """Zahtjev za temperature demo endpoint."""
    prompt: str
    temperature_custom: float = 0.7


class TemperatureResponse(BaseModel):
    """Odgovor temperature demo endpointa."""
    temperatura: float
    tekst: str
    tokeni_input: int
    tokeni_output: int
    trajanje_ms: int


# KORAK 7: Definišemo API endpoint za temperature demo
@app.post("/api/temperature-demo", response_model=List[TemperatureResponse])
async def temperature_demo(zahtjev: TemperatureRequest):
    """
    Šalje isti prompt na tri različite temperature paralelno.

    Vraća tri odgovora istovremeno (async/await za paralelne zahtjeve).
    Ovo je brže nego čekati odgovor jedan po jedan.
    """
    klijent, model = get_llm_client()

    # Tri temperature koje testiramo
    temperature = [0.0, zahtjev.temperature_custom, 1.5]

    async def jedan_poziv(temp: float) -> TemperatureResponse:
        """Jedan API poziv s određenom temperaturom."""
        pocetak = time.monotonic()

        odgovor = await klijent.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    #"content": "Odgovaraj kratko, maksimalno 3 rečenice. Odgovaraj na bosanskom jeziku."
                    "content": "Reply shortly, maximum 3 sentences. Reply in English."
                },
                {
                    "role": "user",
                    "content": zahtjev.prompt
                }
            ],
            temperature=temp,
            max_tokens=150
        )

        kraj = time.monotonic()
        trajanje = int((kraj - pocetak) * 1000)

        return TemperatureResponse(
            temperatura=temp,
            tekst=odgovor.choices[0].message.content,
            tokeni_input=odgovor.usage.prompt_tokens if odgovor.usage else 0,
            tokeni_output=odgovor.usage.completion_tokens if odgovor.usage else 0,
            trajanje_ms=trajanje
        )

    # asyncio.gather = pokreće sve pozive PARALELNO (istovremeno)
    # Umjesto 3x čekanje, čekamo samo onoliko koliko najsporiji traje
    rezultati = await asyncio.gather(*[jedan_poziv(t) for t in temperature])
    return list(rezultati)


@app.get("/api/model-info")
async def model_info():
    """
    Vraća informacije o modelima koji se koriste u treningu.
    Statični endpoint — uvijek vraća iste podatke.
    """
    return {
        "modeli": [
            {
                "naziv": "DeepSeek V3 (cloud)",
                "tip": "cloud",
                "kontekst_tokena": 128000,
                "cijena_input_per_1m": 0.14,
                "cijena_output_per_1m": 0.28,
                "napomena": "Odličan omjer cijena/kvalitet, kineska infrastruktura"
            },
            {
                "naziv": "Llama 3.2 1B (lokalni)",
                "tip": "lokalni",
                "kontekst_tokena": 128000,
                "cijena_input_per_1m": 0.0,
                "cijena_output_per_1m": 0.0,
                "napomena": "Besplatan, privatnost podataka, slabiji kvalitet"
            },
            {
                "naziv": "Llama 3.2 3B (lokalni)",
                "tip": "lokalni",
                "kontekst_tokena": 128000,
                "cijena_input_per_1m": 0.0,
                "cijena_output_per_1m": 0.0,
                "napomena": "Besplatan, bolji od 1B, treba 4GB+ RAM"
            }
        ]
    }


@app.get("/")
async def root():
    """Preusmjerava na index.html."""
    return FileResponse("static/index.html")
