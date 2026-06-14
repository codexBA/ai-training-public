# Docker konfiguracije — AI Trening

Ovaj folder sadrži **zasebne podfoldere** za svaki Docker servis koji se koristi na treningu.
Svaki folder sadrži jedan `docker-compose.yml` koji se pokreće standardnom komandom
`docker compose up -d` — bez ikakvih dodatnih parametara.

---

## Struktura foldera

```
docker/
├── ollama/          ← Samo Ollama LLM server         (port 11434)
│   └── docker-compose.yml
├── sql/             ← Samo SQL Server                 (port 1433)
│   └── docker-compose.yml
├── chroma/          ← Samo ChromaDB vektorska baza    (port 8000)
│   └── docker-compose.yml
├── no-sql/          ← Ollama + ChromaDB (bez SQL-a)
│   └── docker-compose.yml
└── full/            ← Svi servisi zajedno
    └── docker-compose.yml
```

---

## Koji folder, za koji dan i zašto

| Folder | Servisi | Koristi se za |
|---|---|---|
| `docker/ollama/` | Ollama | **Dan 1** (tokeni, temperatura), **Dan 3** (Ollama projekat) |
| `docker/sql/` | SQL Server | Dani s bazama podataka |
| `docker/chroma/` | ChromaDB | RAG / vektorizacija projekti |
| `docker/no-sql/` | Ollama + ChromaDB | **Dan 2** (Film Chat), Dan 4 (Prognoza) |
| `docker/full/` | Sve usluge | Kompletan setup, predavački računar |

---

## Kako pokrenuti

**Važno: `cd` u odgovarajući folder, pa `docker compose up -d`.**

```powershell
# Dan 1 / Dan 3 — samo Ollama
cd docker/ollama
docker compose up -d

# Dan 2 — Ollama + ChromaDB
cd docker/no-sql
docker compose up -d

# Dani s bazama — samo SQL Server
cd docker/sql
docker compose up -d

# Samo ChromaDB
cd docker/chroma
docker compose up -d

# Sve odjednom (predavački računar)
cd docker/full
docker compose up -d
```

---

## Zaustavljanje i čišćenje

```powershell
# Iz foldera koji je pokrenut:
docker compose down           # Zaustavi kontejnere, ČUVA volumene (podatke)
docker compose down -v        # Zaustavi + obriši volumene (NEPOVRATNO!)
docker compose logs -f        # Praćenje logova uživo
docker compose ps             # Status kontejnera u ovom composeu
```

---

## Pregled portova

| Servis | Port | URL |
|---|---|---|
| Ollama | 11434 | http://localhost:11434 |
| SQL Server | 1433 | localhost,1433 |
| ChromaDB | 8000 | http://localhost:8000 |
