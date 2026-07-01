"""
Dan 7 — Projekat 1: Semantička pretraga (ChromaDB + embeddings)

Tok:
  1. Pri startu: chunkovi iz bih_resursi.txt → Chroma kolekcija
  2. Korisnik pošalje upit
  3. Chroma pronađe najsličnije odlomke po značenju (bez LLM-a)

Pokretanje: uvicorn main:app --reload --port 8007
Preduslov: docker/chroma (port 8000)
"""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

from chroma_indeks import indeksiraj, pretrazi
from dokument import DOKUMENT_PATH, podijeli_na_dijelove, ucitaj_dokument

load_dotenv()

TOP_K = 3
BROJ_DIJELOVA = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pri pokretanju: učitaj dokument i indeksiraj u Chroma."""
    global BROJ_DIJELOVA
    dijelovi = podijeli_na_dijelove(ucitaj_dokument(DOKUMENT_PATH))
    print(f"Indeksiranje {len(dijelovi)} odlomaka u Chroma...")
    BROJ_DIJELOVA = indeksiraj(dijelovi)
    print(f"Gotovo — {BROJ_DIJELOVA} odlomaka u kolekciji 'bih_resursi'.")
    yield


app = FastAPI(
    title="Dan 7 — Chroma pretraga",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/api/pretraga")
async def api_pretraga(q: str = Query(..., min_length=1)):
    """Semantička pretraga — vraća odlomke i udaljenost (manja = sličnije)."""
    try:
        pronadeni = pretrazi(q, top_k=TOP_K)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Chroma greška: {exc}") from exc

    return {"upit": q, "pronadeni_dijelovi": pronadeni}
