"""ChromaDB indeksiranje i semantička pretraga (HttpClient + embeddings)."""

import os

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

KOLEKCIJA_IME = "bih_nezaposlenost"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

_embedding_fn: SentenceTransformerEmbeddingFunction | None = None
_kolekcija = None


def get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    """Jedna instanca embedding funkcije (multilingual — bolje za bosanski)."""
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    return _embedding_fn


def get_client() -> chromadb.HttpClient:
    """Povezuje se na ChromaDB server (Docker, port 8000)."""
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8000"))
    try:
        client = chromadb.HttpClient(host=host, port=port)
        client.heartbeat()
        return client
    except Exception as exc:
        raise RuntimeError(
            f"ChromaDB nije dostupan na {host}:{port}. "
            f"Pokrenite: cd docker/chroma && docker compose up -d"
        ) from exc


def get_kolekcija():
    """Vraća Chroma kolekciju (kreira ako ne postoji)."""
    global _kolekcija
    if _kolekcija is None:
        client = get_client()
        _kolekcija = client.get_or_create_collection(
            name=KOLEKCIJA_IME,
            embedding_function=get_embedding_function(),
        )
    return _kolekcija


def indeksiraj(dijelovi: list[str]) -> int:
    """Vektorizira odlomke i sprema u Chroma (upsert — idempotentno)."""
    col = get_kolekcija()
    ids = [str(i) for i in range(len(dijelovi))]
    col.upsert(ids=ids, documents=dijelovi)
    return len(dijelovi)


def pretrazi(upit: str, top_k: int = 2) -> list[dict]:
    """
    Semantička pretraga po značenju.
    Vraća listu dict: tekst, udaljenost (manja = sličnije).
    """
    col = get_kolekcija()
    rez = col.query(query_texts=[upit], n_results=top_k)

    pronadeni: list[dict] = []
    docs = rez.get("documents", [[]])[0]
    distances = rez.get("distances", [[]])[0]

    for tekst, udaljenost in zip(docs, distances):
        pronadeni.append({"tekst": tekst, "udaljenost": round(udaljenost, 4)})

    return pronadeni
