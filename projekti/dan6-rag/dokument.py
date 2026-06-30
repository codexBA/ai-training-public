"""
Ucitavamo dokument i dijelimo na chunkove za RAG
"""

from pathlib import Path

# definisemo putanju do dokumenta
BASE_DIR = Path(__file__).resolve().parent.parent.parent # dobijamo putanju do foldera u kojem se nalazi fajl
DOKUMENT_PATH = BASE_DIR / "podaci" / "bih_turizam.txt"


# ucitaj cijeli dokument i vrati ga kao string
def ucitaj_dokument(putanja: Path=DOKUMENT_PATH) -> str:
    """Ucitava tekst iz dokumenta"""
    with open(putanja, 'r', encoding='utf-8') as fajl: # with automatski zatvara fajl nakon upotrebe
        return fajl.read()

# ova funkcija dijeli tekst na dijelove (chunks) koji su duzi od 30 karaktera i ne pocinju sa "NAPOMENA:" 
def podijeli_na_dijelove(tekst: str) -> list[str]:
    """Podijeli tekst na dijelove"""

    dijelovi: list[str] = []
    for blok in tekst.split("\n\n"):
        blok = blok.strip()

        if(not blok):
            continue

        if blok.startswith("NAPOMENA:"):
            continue

        if len(blok) < 30: # ako je blok kraci od 30 karaktera, preskoci ga
            continue
        
        dijelovi.append(blok)

    return dijelovi

