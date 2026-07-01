# Database API Server (db-api)

Ovaj projekat je REST API (FastAPI) koji komunicira sa `StateStatisticsDB` MS SQL bazom podataka pomoću `pyodbc` biblioteke. Namijenjen je kao pozadinski servis čije će endpointe LLM aplikacija pozivati putem funkcija ("function calling").

## Preduvjeti

1. **SQL Server**: Morate imati instaliran SQL Server.
2. **Baza podataka**: Pokrenite SQL skriptu `setup-database.sql` (iz foldera `sqlskripte`) na vašem SQL Serveru kako biste kreirali bazu i ubacili testne podatke.
3. **Python 3.10+**
4. **ODBC Driver**: Morate imati instaliran "ODBC Driver 17 for SQL Server" (dolazi često uz SQL Server Management Studio).

## Konfiguracija i pokretanje

1. Prekopirajte fajl `.env.example` u fajl `.env`:
   ```bash
   cp .env.example .env
   ```
2. Unutar `.env` fajla provjerite da li `DB_SERVER` odgovara vašem lokalnom serveru (npr. `localhost\SQLEXPRESS`).

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
   uvicorn main:app --host 127.0.0.1 --port 8001 --reload
   ```
   *Napomena: db-api server radi na portu 8001 kako se ne bi sudarao sa chat-api serverom.*

## Swagger Dokumentacija

Kada je server pokrenut, posjetite [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) za testiranje endpointa.
