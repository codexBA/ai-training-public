"""Učitavanje i dijeljenje dokumenta za semantičku pretragu."""

from pathlib import Path

DOKUMENT_PATH = (
    Path(__file__).resolve().parent.parent.parent / "podaci" / "bih_resursi.txt"
)


def ucitaj_dokument(putanja: Path = DOKUMENT_PATH) -> str:
    """Čita tekst dokumenta (UTF-8)."""
    if not putanja.exists():
        raise FileNotFoundError(f"Dokument nije pronađen: {putanja}")
    return putanja.read_text(encoding="utf-8")


def podijeli_na_dijelove(tekst: str) -> list[str]:
    """
    Dijeli tekst na paragrafe (prazni redovi).
    Preskače NAPOMENU na početku i prazne odlomke.
    """
    dijelovi: list[str] = []
    for blok in tekst.split("\n\n"):
        blok = blok.strip()
        if not blok:
            continue
        if blok.startswith("NAPOMENA:"):
            continue
        if len(blok) < 30:
            continue
        dijelovi.append(blok)
    return dijelovi
