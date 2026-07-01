"""
Dan 7 — Projekat 2: RAG s ChromaDB (semantička pretraga + LLM)

Tok:
  1. Pri startu: chunkovi iz bih_nezaposlenost.txt → Chroma kolekcija
  2. Korisnik postavi pitanje
  3. Chroma pronađe relevantne odlomke (embedding)
  4. LLM odgovori samo na osnovu pronađenog konteksta

Pokretanje: uvicorn main:app --reload --port 8071
Preduslov: docker/chroma (port 8000)
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from chroma_indeks import indeksiraj, pretrazi
from dokument import DOKUMENT_PATH, podijeli_na_dijelove, ucitaj_dokument

load_dotenv()

TOP_K = 2

SYSTEM = (
    "Ti si asistent."
    "Odgovaraj SAMO na osnovu KONTEKSTA ispod. "
    "Ako odgovor nije u kontekstu, reci: 'U dokumentu nemam tu informaciju.'."
    "Nemoj izmisljati ako kontekst ne sadrzi trazeni podatak."
    "Odgovaraj kratko na bosanskom, hrvatskom ili srpskom jeziku."
)


def get_llm_client():
    """Povezuje se na LLM prema .env — deepseek ili ollama."""
    provider = os.getenv("LLM_PROVIDER", "deepseek").strip().lower()

    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key or api_key == "sk-vas-kljuc-ovdje":
            raise RuntimeError("U .env postavite DEEPSEEK_API_KEY")
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        return client, "deepseek-chat"

    if provider == "ollama":
        url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        client = AsyncOpenAI(api_key="ollama", base_url=f"{url}/v1")
        return client, model

    raise RuntimeError(f"Nepoznat LLM_PROVIDER: {provider!r}")


async def pitaj_rag(
    client, model: str, pitanje: str, temperatura: float
) -> tuple[str, list[dict]]:
    """RAG: Chroma pretraga → kontekst → jedan LLM poziv."""
    pronadeni = pretrazi(pitanje, top_k=TOP_K)

    if pronadeni:
        kontekst = "\n\n---\n\n".join(d["tekst"] for d in pronadeni)
        user_sadrzaj = f"KONTEKST:\n{kontekst}\n\nPITANJE: {pitanje}"
    else:
        user_sadrzaj = (
            f"KONTEKST:\n(nema pronađenih odlomaka)\n\nPITANJE: {pitanje}"
        )

    odgovor = await client.chat.completions.create(
        model=model,
        temperature=temperatura,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_sadrzaj},
        ],
    )
    tekst = (odgovor.choices[0].message.content or "").strip()
    return tekst, pronadeni


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pri pokretanju: učitaj dokument i indeksiraj u Chroma."""
    dijelovi = podijeli_na_dijelove(ucitaj_dokument(DOKUMENT_PATH))
    print(f"Indeksiranje {len(dijelovi)} odlomaka u Chroma...")
    broj = indeksiraj(dijelovi)
    print(f"Gotovo — {broj} odlomaka u kolekciji 'bih_nezaposlenost'.")
    yield


app = FastAPI(
    title="Dan 7 — RAG Chroma",
    version="1.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    poruka: str = Field(min_length=1)
    temperatura: float = Field(default=0.3, ge=0.0, le=1.5)


class ChatResponse(BaseModel):
    odgovor: str
    pronadeni_dijelovi: list[dict]


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(zahtjev: ChatRequest):
    try:
        client, model = get_llm_client()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        odgovor, pronadeni = await pitaj_rag(
            client, model, zahtjev.poruka, zahtjev.temperatura
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM greška: {exc}") from exc

    return ChatResponse(odgovor=odgovor, pronadeni_dijelovi=pronadeni)
