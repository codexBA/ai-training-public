# Chat API Server (chat-api)

Ovaj projekat je REST API (FastAPI) zadužen za komunikaciju sa LLM modelom (DeepSeek ili Ollama). Definira alate ("function calling") koji LLM modelu omogućuju dohvatanje podataka. Kada model zatraži poziv funkcije, ovaj API interno izvršava HTTP zahtjev prema `db-api` serveru i vraća rezultat modelu.

## Preduvjeti

1. **Python 3.10+**
2. **LLM**: Pristup Ollama (lokalno) ili DeepSeek API ključu.
3. Pokrenut **db-api** server na `http://127.0.0.1:8001`.

## Konfiguracija i pokretanje

1. Prekopirajte fajl `.env.example` u fajl `.env`:
   ```bash
   cp .env.example .env
   ```
2. Unutar `.env` fajla konfigurirajte koji LLM provajder želite koristiti i postavite ključeve ako je potrebno.

3. Kreirajte i aktivirajte virtualno okruženje:
   ```bash
   python -m venv venv
   # Za Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   ```

4. Instalirajte zavisnosti:
   ```bash
   pip install -r requirements.txt
   ```

5. Pokrenite server:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

Server će biti dostupan na [http://127.0.0.1:8000](http://127.0.0.1:8000). Endpoint za komunikaciju iz frontenda je `POST /api/chat`.
