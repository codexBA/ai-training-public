"""
Mini-projekat: AI Debata — Gradovi BiH
Svrha: AI generira humoristične kritike i komplimente za bosanske gradove,
       te organizira debate između dva grada.

Pokretanje:
    uvicorn main:app --reload --port 8014
"""

import asyncio
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

app = FastAPI(
    title="Mini-projekat — AI Debata",
    description="AI generira humoristične kritike i komplimente za gradove BiH",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

GRADOVI = [
    "Sarajevo", "Tuzla", "Banja Luka", "Brčko", "Mostar",
    "Trebinje", "Bihać", "Zenica", "Stolac",
]


# ---------------------------------------------------------------------------
# LLM klijent — isti fallback pattern kao u svim projektima
# ---------------------------------------------------------------------------

def get_llm_client():
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if api_key and api_key != "sk-vas-kljuc-ovdje":
        return AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1"), "deepseek-chat"
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
    return AsyncOpenAI(api_key="ollama", base_url=f"{ollama_url}/v1"), model


# ---------------------------------------------------------------------------
# Pydantic modeli
# ---------------------------------------------------------------------------

class KritikaRequest(BaseModel):
    grad: str = "Sarajevo"
    stil: str = "srednji"  # "blagi" | "srednji" | "brutalni"


class KritikaResponse(BaseModel):
    tekst: str
    grad: str
    stil: str
    model: str


class PohvalaRequest(BaseModel):
    grad: str = "Sarajevo"


class PohvalaResponse(BaseModel):
    tekst: str
    grad: str
    model: str


class DebataRequest(BaseModel):
    grad1: str = "Sarajevo"
    grad2: str = "Mostar"


class DebataResponse(BaseModel):
    kritika1: str
    kritika2: str
    grad1: str
    grad2: str
    model: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/kritikuj", response_model=KritikaResponse)
async def kritikuj(req: KritikaRequest):
    client, model = get_llm_client()

    system_prompt = (
        f"Ti si stand-up komičar iz Bosne i Hercegovine. "
        f"Tvoj zadatak je da na duhovit način kritikuješ grad {req.grad}.\n\n"
        f"Stil: {req.stil}\n"
        "- \"blagi\" = nježne šale, kao da pričaš s prijateljem iz tog grada\n"
        "- \"srednji\" = oštrije šale, ali s ljubavlju\n"
        "- \"brutalni\" = bezobrazne šale (ali NIKAD uvredljive na nacionalnoj/vjerskoj/etničkoj osnovi!)\n\n"
        "Pravila:\n"
        "1. Koristi lokalne reference (kafane, ulice, navike, vremensku prognozu, saobraćaj...)\n"
        "2. Budi duhovit, ne uvredljiv — cilj je da se svi smiju, uključujući ljude iz tog grada\n"
        "3. Maksimalno 4-5 rečenica\n"
        "4. Piši na bosanskom jeziku\n"
        "5. Koristi humor prepoznatljiv ljudima iz BiH"
    )

    response = await client.chat.completions.create(
        model=model,
        temperature=1.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Kritikuj grad {req.grad} u stilu: {req.stil}."},
        ],
    )

    tekst = response.choices[0].message.content.strip()

    return KritikaResponse(tekst=tekst, grad=req.grad, stil=req.stil, model=model)


@app.post("/api/pohvali", response_model=PohvalaResponse)
async def pohvali(req: PohvalaRequest):
    client, model = get_llm_client()

    system_prompt = (
        f"Ti si pjesnik koji je beznadežno zaljubljen u grad {req.grad}. "
        f"Napiši najljepši, najentuzijastičniji kompliment za ovaj grad. "
        f"Koristi lokalne reference, historiju, ljepotu, ljude. "
        f"4-5 rečenica na bosanskom. Budi poetičan ali ne pretjerano formalan."
    )

    response = await client.chat.completions.create(
        model=model,
        temperature=0.9,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Napiši kompliment za grad {req.grad}."},
        ],
    )

    tekst = response.choices[0].message.content.strip()

    return PohvalaResponse(tekst=tekst, grad=req.grad, model=model)


@app.post("/api/debata", response_model=DebataResponse)
async def debata(req: DebataRequest):
    client, model = get_llm_client()

    def _system(grad_iz, grad_protiv):
        return (
            f"Ti si stand-up komičar iz grada {grad_iz}. "
            f"Kritikuj grad {grad_protiv} iz perspektive stanovnika {grad_iz}. "
            f"Koristi rivalstvo između ova dva grada. "
            f"Budi duhovit, ne uvredljiv. 3-4 rečenice na bosanskom. "
            f"NIKAD uvrede na nacionalnoj/vjerskoj/etničkoj osnovi!"
        )

    async def _call(grad_iz, grad_protiv):
        resp = await client.chat.completions.create(
            model=model,
            temperature=1.0,
            messages=[
                {"role": "system", "content": _system(grad_iz, grad_protiv)},
                {"role": "user", "content": f"Kritikuj {grad_protiv} iz perspektive {grad_iz}."},
            ],
        )
        return resp.choices[0].message.content.strip()

    # Dva paralelna LLM poziva
    kritika1, kritika2 = await asyncio.gather(
        _call(req.grad1, req.grad2),
        _call(req.grad2, req.grad1),
    )

    return DebataResponse(
        kritika1=kritika1,
        kritika2=kritika2,
        grad1=req.grad1,
        grad2=req.grad2,
        model=model,
    )
