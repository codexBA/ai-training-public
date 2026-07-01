"""
ChromaDB indeksiranje i semantička pretraga (HttpClient + embeddings).

SVRHA I NAČIN RADA:
1. Skripta služi za pohranjivanje tekstualnih odlomaka i njihovu semantičku pretragu na osnovu značenja (ne samo ključnih riječi).
2. Embedding model (`paraphrase-multilingual-MiniLM-L12-v2`) se pokreće LOKALNO:
   - Prilikom prvog pokretanja, biblioteka `sentence-transformers` automatski preuzima ovaj model sa Hugging Face-a na lokalni disk.
   - Vektorizacija (kreiranje embeddinga) se izvršava lokalno na mašini koja pokreće ovaj Python klijent.
3. ChromaDB baza se hostuje zasebno na DOCKERU (obično na portu 8000).
   - Python klijent se povezuje na ChromaDB server putem `HttpClient`-a.
   - Kod slanja i pretraživanja dokumenata, klijent lokalno izračunava vektore, a zatim ih šalje na ChromaDB server na čuvanje ili poređenje.
"""

# Uvoz biblioteke os za rad sa sistemskim varijablama okruženja
import os

# Uvoz klijenta za rad sa ChromaDB vektorskom bazom podataka
import chromadb
# Uvoz klase koja omogućava kreiranje embeddinga (vektora) lokalno pomoću SentenceTransformer modela
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Naziv kolekcije u ChromaDB bazi u koju ćemo spremati podatke
KOLEKCIJA_IME = "bih_resursi"
# Identifikator modela sa Hugging Face-a koji podržava više jezika (uključujući bosanski/srpski/hrvatski)
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Globalne varijable koje služe kao keš (singleton) da ne bismo stalno ponovo inicijalizirali model i kolekciju
_embedding_fn: SentenceTransformerEmbeddingFunction | None = None
_kolekcija = None

# ova funkcija dohvatamo embedding model koji je odgovoran za pretvaranje teksta u vektore
def get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    """Jedna instanca embedding funkcije (multilingual — bolje za bosanski)."""
    global _embedding_fn
    # Ako model još nije učitan u memoriju, inicijaliziramo ga
    if _embedding_fn is None:
        # Inicijalizacija SentenceTransformerEmbeddingFunction-a. 
        # Prilikom prvog pokretanja, biblioteka će automatski preuzeti model sa Hugging Face-a na lokalni disk.
        _embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    return _embedding_fn

#ova funkcija nam sluzi za povezivanje sa ChromaDB serverom
def get_client() -> chromadb.HttpClient:
    """Povezuje se na ChromaDB server (Docker, port 8000)."""
    # Čitamo adresu hosta i port iz varijabli okruženja, sa podrazumijevanim vrijednostima 'localhost' i 8000
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8000"))
    try:
        # Inicijalizacija klijenta koji komunicira sa ChromaDB serverom preko HTTP protokola
        client = chromadb.HttpClient(host=host, port=port)
        # Provjera da li je server aktivan (šalje kratak signal za provjeru rada)
        client.heartbeat()
        return client
    except Exception as exc:
        # Ako server nije dostupan (npr. Docker kontejner nije pokrenut), ispisujemo jasnu grešku sa uputstvom
        raise RuntimeError(
            f"ChromaDB nije dostupan na {host}:{port}. "
            f"Pokrenite: cd docker/chroma && docker compose up -d"
        ) from exc

#ova funkcija nam sluzi za dohvatavanje kolekcije u ChromaDB bazi podataka,ako ne postoji onda se kreira
def get_kolekcija():
    """Vraća Chroma kolekciju (kreira ako ne postoji)."""
    global _kolekcija
    # Ako nismo ranije dohvatili kolekciju, radimo to sada
    if _kolekcija is None:
        # Povezujemo se na klijent
        client = get_client()
        # Dohvaćamo postojeću kolekciju ili kreiramo novu. 
        # Ovdje povezujemo kolekciju sa našom embedding funkcijom (modelom) kako bi Chroma znala kako pretvoriti tekst u vektore.
        _kolekcija = client.get_or_create_collection(
            name=KOLEKCIJA_IME,
            embedding_function=get_embedding_function(),
        )
    return _kolekcija

#ova funkcija nam sluzi za indeksiranje podataka u ChromaDB bazi podataka
def indeksiraj(dijelovi: list[str]) -> int:
    """Vektorizira odlomke i sprema u Chroma (upsert — idempotentno)."""
    # Dohvaćamo kolekciju
    col = get_kolekcija()
    # Generišemo jednostavne ID-eve za svaki dio teksta (npr. ["0", "1", "2", ...])
    ids = [str(i) for i in range(len(dijelovi))]
    # upsert metoda dodaje nove dokumente ili ažurira postojeće ako već imaju isti ID.
    # Prije slanja na server, klijent koristi get_embedding_function() da lokalno kreira vektore za ove dokumente.
    col.upsert(ids=ids, documents=dijelovi)
    return len(dijelovi)


#ova funkcija nam sluzi za pretragu podataka u ChromaDB bazi podataka,vraca listu dict: tekst, udaljenost (manja = sličnije).
def pretrazi(upit: str, top_k: int = 3) -> list[dict]:
    """
    Semantička pretraga po značenju (ne po ključnim riječima).
    Vraća listu dict: tekst, udaljenost (manja = sličnije).
    """
    # Dohvaćamo kolekciju
    col = get_kolekcija()
    # query metoda vrši pretragu. Tekst upita se lokalno pretvara u vektor pomoću embedding funkcije,
    # a zatim se taj vektor šalje na ChromaDB server koji pronalazi najsličnije vektore u bazi.
    rez = col.query(query_texts=[upit], n_results=top_k)

    pronadeni: list[dict] = []
    # Izdvajamo dokumente i njihove udaljenosti (kosinusna/L2 udaljenost) iz rezultata pretrage
    docs = rez.get("documents", [[]])[0]
    distances = rez.get("distances", [[]])[0]

    # Spajamo dokumente i udaljenosti te ih formatiramo u čitljivu listu rječnika
    for tekst, udaljenost in zip(docs, distances):
        pronadeni.append({"tekst": tekst, "udaljenost": round(udaljenost, 4)})

    return pronadeni