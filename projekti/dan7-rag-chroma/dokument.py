"""Učitavanje i dijeljenje dokumenta za RAG s Chroma pretragom."""

import re
from pathlib import Path

DOKUMENT_PATH = (
    Path(__file__).resolve().parent.parent.parent / "podaci" / "bih_nezaposlenost.md"
)


def ucitaj_dokument(putanja: Path = DOKUMENT_PATH) -> str:
    """Čita tekst dokumenta (UTF-8)."""
    if not putanja.exists():
        raise FileNotFoundError(f"Dokument nije pronađen: {putanja}")
    return putanja.read_text(encoding="utf-8")


def podijeli_na_dijelove(tekst: str) -> list[str]:
    """
    Optimalno dijeli markdown dokument na cjeline za vektorizaciju.
    Zadržava strukturu tabela i cjelovitost sekcija (dijeli po ##).
    """
    dijelovi: list[str] = []
    # Dijelimo tekst prije svakog naslova 2. nivoa, čuvajući naslov unutar bloka
    blokovi = re.split(r'\n(?=## )', tekst)
    
    for blok in blokovi:
        blok = blok.strip()
        # Uklanjanje horizontalnih linija koje razdvajaju sekcije
        blok = re.sub(r'\n\s*---\s*\n', '\n\n', blok)
        blok = blok.strip()
        
        if not blok:
            continue
        if len(blok) < 30:
            continue
            
        dijelovi.append(blok)
    return dijelovi
