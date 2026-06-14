# Dan 1 — Token Vizualizator i Temperature Playground

## Svrha

Ovaj projekat demonstrira tri osnovna koncepta rada s LLM modelima:
1. **Tokenizacija** — kako LLM "vidi" tekst (dijeli ga na tokene)
2. **Temperatura** — kako parametar temperature utječe na kreativnost odgovora
3. **API pozivi** — kako komunicirati s LLM-om programski (DeepSeek/Ollama)

## Dva klijenta — obavezno

Svaki projekat obuke mora imati **dva načina korištenja**:

| Klijent | Lokacija | Namjena |
|---------|----------|---------|
| **Web** | `static/` + backend na portu **8001** | Demo za studente, hosting, vizualni prikaz (npr. demo-1.erkanislamovic.com) |
| **Konzola (CLI)** | `cli/tokenizer_cli.py`, `cli/temperature_cli.py` | Učenje, testiranje bez browsera, debug API poziva |

Oba koriste isti backend (`main.py`) ili istu logiku (tiktoken / OpenAI SDK). Web šalje HTTP zahtjeve na FastAPI; CLI poziva API direktno iz Pythona.

### Redoslijed pokretanja

1. **Backend prvo** — `uvicorn main:app --reload --port 8001` (ili `docker compose up --build`)
2. **Web** — otvorite http://localhost:8001 u browseru
3. **CLI** — u drugom terminalu (venv aktivan): `python cli\tokenizer_cli.py` ili `python cli\temperature_cli.py`

| Servis | URL / komanda | Port |
|--------|---------------|------|
| Web UI | http://localhost:8001 | 8001 |
| API docs (Swagger) | http://localhost:8001/docs | 8001 |
| Token CLI | `python cli\tokenizer_cli.py` | — (offline) |
| Temperature CLI | `python cli\temperature_cli.py` | — (DeepSeek ili Ollama) |

Puni korak-po-korak vodič: **[docs/dan1.html](../../docs/dan1.html)** (Blok 3 i 3B).

## Pedagoški cilj

Nakon ovog projekta polaznik treba razumjeti:
- Šta su tokeni i zašto bosanski tekst troši više tokena od engleskog
- Kako temperatura mijenja ponašanje modela (0=deterministički, 1.5=kreativno)
- Kako se računa cijena API poziva (input tokeni + output tokeni × cijena)
- Kako napraviti prvi API poziv prema LLM-u iz Pythona
- Šta je kontekst prozor i zašto je ograničen

## Prerequisites

- [ ] Docker Desktop instaliran i pokrenut
- [ ] Python 3.11 / 3.12 / 3.13 instaliran
- [ ] `.env` fajl kreiran (kopirajte `.env.example` u `.env`)
- [ ] DeepSeek API key ILI pokrenut Ollama server (barem jedno od dva)

## Kako pokrenuti

### Opcija A — Docker (preporučeno)

```bash
cd projekti/dan1-tokeni
cp .env.example .env
# Uredite .env i dodajte DEEPSEEK_API_KEY (ili ostavite za Ollama fallback)
docker-compose up --build
```

Otvorite browser: **http://localhost:8001**

### Opcija B — Lokalno bez Dockera

```bash
cd projekti/dan1-tokeni
cp .env.example .env
# Uredite .env i dodajte DEEPSEEK_API_KEY

pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Otvorite browser: **http://localhost:8001**

## Kako testirati da radi

### 1. Web interfejs

Otvorite http://localhost:8001 u browseru. Trebate vidjeti:
- Token Vizualizator — unesite tekst, kliknite "Analiziraj tokene"
- Temperature Playground — unesite prompt, kliknite "Pokreni eksperiment"
- Tabela usporedbe modela na dnu stranice

### 2. API endpoints

```bash
# Model info (uvijek radi, ne zahtijeva API key)
curl http://localhost:8001/api/model-info

# Temperature demo (zahtijeva API key ili Ollama)
curl -X POST http://localhost:8001/api/temperature-demo \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Šta je AI?", "temperature_custom": 0.7}'
```

### 3. Jupyter notebook

```bash
cd projekti/dan1-tokeni/notebooks
jupyter lab
# Otvorite dan1_tokeni.ipynb
# Pokrenite ćelije redom: Shift+Enter
```

## Struktura projekta

```
dan1-tokeni/
├── main.py                  ← FastAPI backend (API endpointi)
├── static/                  ← WEB KLIJENT
│   ├── index.html           ← Web UI (dark tema)
│   ├── style.css            ← Stilovi za web UI
│   └── app.js               ← Token aproksimacija + API pozivi
├── cli/                     ← KONZOLNI KLIJENTI
│   ├── tokenizer_cli.py     ← Token analizator (offline, tiktoken)
│   └── temperature_cli.py   ← Temperature eksperiment (API)
├── notebooks/
│   └── dan1_tokeni.ipynb    ← Jupyter notebook (tiktoken + eksperimenti)
├── requirements.txt         ← Python zavisnosti
├── Dockerfile               ← Docker konfiguracija
├── docker-compose.yml       ← Docker Compose za projekat
├── .env.example             ← Template za environment varijable
├── README.md                ← Ovaj fajl
└── INSTALACIJA.md           ← Korak-po-korak instalacijski vodič
```

## Ključni koncepti koje projekt demonstrira

| Koncept | Objašnjenje |
|---------|-------------|
| **Token** | Osnovna jedinica teksta za LLM (~4 znaka EN, ~2.5 znaka BS) |
| **Tokenizacija** | Proces dijeljenja teksta na tokene koje model može obraditi |
| **Temperatura** | Parametar (0.0-2.0) koji kontroliše nasumičnost odgovora |
| **Kontekst prozor** | Maksimalan broj tokena koji model može "vidjeti" odjednom |
| **API cijena** | Formula: (input_tokeni + output_tokeni) × cijena_per_1M |
| **Fallback** | Automatsko prebacivanje s DeepSeek API-ja na lokalni Ollama |

## Česte greške i rješenja

### Greška: "Port 8001 already in use"
**Rješenje:** Zaustavite proces koji koristi port:
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <pid> /F

# Ili promijenite port u docker-compose.yml i .env
```

### Greška: "Ni DeepSeek API ni Ollama nisu dostupni"
**Rješenje:** Morate imati barem jedno od dva:
- Postavite `DEEPSEEK_API_KEY` u `.env` fajl, ILI
- Pokrenite Ollama: `docker-compose -f ../../docker-compose.yml up -d ollama`

### Greška: ".env fajl ne postoji"
**Rješenje:** Kopirajte template:
```bash
cp .env.example .env
```

### Greška: "ModuleNotFoundError: No module named 'tiktoken'"
**Rješenje:** Instalirajte zavisnosti:
```bash
pip install -r requirements.txt
```

## Zaključci i sljedeći koraci

**Naučili smo:**
- LLM modeli ne rade s riječima nego s tokenima
- Bosanski tekst je "skuplji" od engleskog (više tokena po riječi)
- Temperatura kontroliše kreativnost vs konzistentnost odgovora
- API fallback osigurava da vježbe rade i bez cloud API-ja

**Sljedeće:** Dan 2 — Chat aplikacija s historijom razgovora, JSON baza filmova i usporedba modela.
