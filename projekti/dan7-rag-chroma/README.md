# Dan 7 - RAG s ChromaDB (Semantička pretraga + LLM)

Ovaj projekat demonstrira implementaciju **RAG** (Retrieval-Augmented Generation) sistema koristeći **ChromaDB** za vektorsku bazu podataka i **FastAPI** za kreiranje API-ja. Aplikacija omogućava semantičku pretragu nad tekstualnim dokumentom (u ovom slučaju podacima o nezaposlenosti u BiH) i generisanje odgovora isključivo na osnovu pronađenog konteksta pomoću LLM-a (DeepSeek ili Ollama lokalno).

## 🚀 Mogućnosti

- **Automatsko indeksiranje**: Pri pokretanju servera, dokument se automatski dijeli na smislene cjeline (chunkove) i indeksira u Chroma bazu.
- **Semantička pretraga**: Korisnikov upit se vektorizuje pomoću višejezičnog embedding modela (`paraphrase-multilingual-MiniLM-L12-v2`), a zatim pronalaze najsličniji odlomci teksta.
- **Kontekstualni odgovori**: LLM odgovara na pitanja isključivo bazirano na proslijeđenom kontekstu iz baze, bez "halucinacija".
- **Podrška za više LLM provajdera**: Konfiguracija kroz `.env` datoteku (podrška za DeepSeek preko API-ja ili lokalni model preko Ollame).

## 🛠️ Arhitektura (Kako radi)

1. **Čitanje dokumenta**: `dokument.py` učitava markdown fajl i dijeli ga na sekcije (pazeći na cjelovitost naslova druge razine `##`).
2. **Indeksiranje (Vektorizacija)**: `chroma_indeks.py` koristi `SentenceTransformerEmbeddingFunction` da pretvori tekst u vektore i sačuva ih u instancu ChromaDB-a.
3. **Pretraga**: Kada korisnik pošalje upit putem FastAPI endpointa, on se šalje u bazu, iz koje se vraćaju najrelevantniji odlomci teksta (po zadanoj vrijednosti `TOP_K = 2`).
4. **Generisanje odgovora (LLM)**: FastAPI (`main.py`) šalje pronalaske i originalni upit LLM-u, uz jasnu "sistemsku uputu" da odgovara *samo* iz tog konteksta.

## 📁 Struktura projekta

- `main.py` - Glavna FastAPI aplikacija sa definisanim rutama i RAG logikom.
- `chroma_indeks.py` - Povezivanje na ChromaDB, definicija embedding modela, spremanje teksta i semantička pretraga.
- `dokument.py` - Učitavanje izvornog `.md` dokumenta te njegovo "sjeckanje" (chunking) na manje, smislene dijelove.
- `.env` - Konfiguracijski fajl za API ključeve i postavke baze/LLM-a (ne verzionira se).
- `static/index.html` - Jednostavan web korisnički interfejs za testiranje RAG-a.

## ⚙️ Preduslovi

1. **Python 3.10+**
2. **Docker** (za pokretanje ChromaDB servera)
3. **Instalirane biblioteke** (`pip install -r requirements.txt` ili u okviru postojećeg okruženja projekta).
   - `fastapi`, `uvicorn`, `chromadb`, `sentence-transformers`, `openai`, `pydantic`, `python-dotenv`.

## 🚀 Pokretanje

### 1. Pokretanje Chroma baze

Baza mora biti pokrenuta prije API-ja. Ako imate `docker/chroma` direktorij u root-u svog repozitorija, pređite tamo i pokrenite bazu:

```bash
cd putanja/do/docker/chroma
docker compose up -d
```
Chroma će se pokrenuti na portu `8000`.

### 2. Konfiguracija (.env)

Kreirajte `.env` fajl u direktoriju projekta (`dan7-rag-chroma/.env`) i popunite ga podacima prema vašim potrebama:

```env
# LLM Konfiguracija (deepseek ili ollama)
LLM_PROVIDER=deepseek

# Za DeepSeek
DEEPSEEK_API_KEY=sk-vas-kljuc-ovdje

# Za Ollamu (ako se koristi lokalno)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

# Chroma postavke
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

### 3. Pokretanje API servera

Pozicionirajte se u direktorij projekta (`dan7-rag-chroma`) i pokrenite FastAPI server:

```bash
python -m uvicorn main:app --reload --port 8072
```

*(Napomena: server će se podići i automatski indeksirati dokumente iz podaci/bih_nezaposlenost.md)*

### 4. Korištenje i testiranje

Otvorite vaš web pretraživač i posjetite:
👉 **[http://localhost:8072/](http://localhost:8072/)**

Tu vas čeka jednostavan web interfejs preko kojeg možete slati pitanja. Ako u terminalu vidite "Indeksiranje... Gotovo", to znači da je baza napunjena i spremna.
