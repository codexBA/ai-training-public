# AI Trening — Advanced Application of LLMs and AI Tools in IT

7-dnevna obuka za IT inžinjere u državnim institucijama Bosne i Hercegovine.

**Predavač:** Erkan Islamović  
**Trajanje:** 7 dana × 7-8 sati  
**Nivo:** Srednji (IT iskustvo, osnove Pythona i SQL-a)

---

## Quick Start

### 1. Klonirajte repozitorij

```bash
git clone <repo-url>
cd ai-trening
```

### 2. Pokrenite infrastrukturu

```bash
docker-compose up -d
```

> **Napomena:** Ukoliko već imate instaliran SQL Server na svom računaru, gornja komanda će vjerovatno prijaviti grešku zbog zauzetog porta `1433`. U tom slučaju, umjesto gornje, koristite ovu komandu:
> ```bash
> docker-compose -f docker-compose.no-sql.yml up -d
> ```

Ovo pokreće tri servisa:
- **SQL Server 2022** na portu `1433`
- **Ollama** (lokalni LLM) na portu `11434`
- **ChromaDB** (vektorska baza) na portu `8000`

### 3. Provjerite da sve radi

```bash
docker ps
# Trebate vidjeti 3 running kontejnera:
#   ai-trening-sqlserver
#   ai-trening-ollama
#   ai-trening-chromadb
```

### 4. Otvorite dokumentaciju

Otvorite `docs/index.html` u browseru — to je naslovna stranica s kompletnim sadržajem obuke.

**Dan 1** (`docs/dan1.html`) i **Dan 2** (`docs/dan2.html`) sadrže kompletne 7-satne vodiče (satnica, teorija, korak-po-korak praksa, vježbe). Ostali dani: vidi [docs/DOC_STANDARDS.md](docs/DOC_STANDARDS.md).

### Pravilo svih projekata (Dan 1–7): Web + konzola

Svaki projekat obuke (`projekti/danX-*`) mora imati **dva načina korištenja**:

| Klijent | Folder | Namjena |
|---------|--------|---------|
| **Web** | `static/` + FastAPI backend | Demo studentima, hosting (npr. demo-X.erkanislamovic.com), vizualni UI |
| **Konzola (CLI)** | `cli/*.py` | Učenje, debug, test bez browsera, automatizacija |

Oba dijele isti backend (`main.py`) ili istu logiku (API / tiktoken). Detalji u README svakog projekta i u [instructions.md](instructions.md).

---

## Struktura projekta

```
ai-trening/
│
├── docs/                          ← HTML dokumentacija (9 fajlova)
│   ├── index.html                 ← Naslovna, sadržaj, glosar
│   ├── dan1.html                  ← Tokeni, temperatura, LLM osnove
│   ├── dan2.html                  ← Chat, JSON baza, API, historija
│   ├── dan3.html                  ← Ollama, lokalni LLM, Docker
│   ├── dan4.html                  ← Function calling, prognoza
│   ├── dan5.html                  ← Vektorizacija, embeddings, RAG
│   ├── dan6.html                  ← SQL Server, pandas, AI analiza
│   ├── dan7.html                  ← Finalni projekti, smjerovi
│   ├── zakljucci.html             ← Sumarna poglavlja, smjernice
│   ├── style.css                  ← Zajednički stil (dark tema)
│   └── nav.js                     ← Navigacija, search, progress
│
├── projekti/                      ← Kod projekata (po danima)
│   ├── dan0-setup/                ← Preduslovi i instalacija
│   ├── dan1-tokeni/               ← Token vizualizator
│   ├── dan2-film-chat/            ← Chat aplikacija s filmovima
│   ├── dan3-ollama/               ← Lokalni LLM eksperimenti
│   ├── dan4-prognoza/             ← Function calling + prognoza
│   ├── dan5-rag/                  ← RAG nad BiH dokumentima
│   ├── dan6-baza/                 ← SQL + AI analiza podataka
│   └── dan7-finalni/              ← Finalni projekti (3 smjera)
│
├── podaci/                        ← Zajednički dataseti
│   ├── filmovi.json               ← 40 filmova za Dan 2
│   ├── bih_turizam.txt            ← BiH turizam (za RAG)
│   ├── bih_ekonomija.txt          ← BiH ekonomija (za RAG)
│   └── bih_resursi.txt            ← BiH resursi (za RAG)
│
├── docker-compose.yml             ← Root compose (SQL+Ollama+ChromaDB)
├── .gitignore
└── README.md                      ← Ovaj fajl
```

---

## Raspored obuke

| Dan | Tema | Projekt |
|-----|------|---------|
| 0 | Priprema okruženja (dan prije obuke) | `dan0-setup` |
| 1 | Tokeni, temperatura, LLM osnove | `dan1-tokeni` |
| 2 | Chat, JSON baza, API, historija razgovora | `dan2-film-chat` |
| 3 | Ollama: lokalni LLM server | `dan3-ollama` |
| 4 | Function calling: AI koji koristi alate | `dan4-prognoza` |
| 5 | Vektorizacija, embeddings i RAG | `dan5-rag` |
| 6 | SQL Server, pandas i AI analiza | `dan6-baza` |
| 7 | Finalni projekti i prezentacije | `dan7-finalni` |

---

## Tehnički stack

| Alat | Namjena | Port |
|------|---------|------|
| DeepSeek API | Cloud LLM (primarni) | — |
| Ollama | Lokalni LLM (fallback / privatnost) | 11434 |
| ChromaDB | Vektorska baza za RAG | 8000 |
| SQL Server 2022 | Relacijska baza podataka | 1433 |
| FastAPI | Python web framework (backend) | 8001 |
| Docker | Kontejnerizacija svih servisa | — |

---

## Preduslovi

Detaljne upute za instalaciju svih alata nalazite u:
**[projekti/dan0-setup/DAN0_SETUP.md](projekti/dan0-setup/DAN0_SETUP.md)**

Ukratko:
- Git 2.x+
- Python 3.11 / 3.12 / 3.13
- Docker Desktop 4.x+
- ODBC Driver 17 ili 18 for SQL Server

---

## Kontakt

Za pitanja i podršku obratite se predavaču: **Erkan Islamović**
