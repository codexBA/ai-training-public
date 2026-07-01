# AI Državna Statistika - dan7-finale

Ovaj projekat predstavlja cjelokupni sistem za analizu i chat sa bazom podataka državne statistike pomoću LLM-a i mehanizma pozivanja funkcija (Function Calling/Tools).

Sistem se sastoji od tri zasebne komponente locirane u sljedećim direktorijima:
1. **[db-api](file:///x:/Projects/GitHub/AI-Training-public/projekti/dan7-finale/db-api)** - FastAPI server koji se povezuje na SQL Server bazu podataka i pruža REST endpointe.
2. **[chat-api](file:///x:/Projects/GitHub/AI-Training-public/projekti/dan7-finale/chat-api)** - FastAPI server za komunikaciju sa LLM modelom koji poziva alate iz `db-api` i šalje odgovore korisniku.
3. **[frontend](file:///x:/Projects/GitHub/AI-Training-public/projekti/dan7-finale/frontend)** - Korisnički interfejs (Vanilla HTML, CSS, JS) za interakciju sa chat sistemom.

---

## Redoslijed konfiguracije i pokretanja

Za ispravan rad sistema, konfiguraciju i pokretanje projekata izvršite tačno ovim redoslijedom:

### Korak 1: Konfiguracija i pokretanje baze podataka
Prije pokretanja bilo kojeg API-ja, osigurajte da je SQL Server baza spremna:
1. Pokrenite SQL skriptu iz fajla `sqlskripte/setup-database.sql` na svom SQL Serveru kako biste kreirali bazu podataka `StateStatisticsDB` sa testnim podacima.

---

### Korak 2: Konfiguracija i pokretanje `db-api` servera
Ovaj server mora se pokrenuti prvi kako bi `chat-api` mogao raditi provjeru i pozivanje alata.
1. Otvorite terminal u folderu `projekti/dan7-finale/db-api`.
2. Kreirajte `.env` fajl na osnovu `.env.example` i unesite parametre za konekciju na SQL Server.
3. Kreirajte i aktivirajte virtualno okruženje, te instalirajte pakete:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
4. Pokrenite server na željenom portu (npr. **8073**):
   ```powershell
   uvicorn main:app --host 127.0.0.1 --port 8073 --reload
   ```

---

### Korak 3: Konfiguracija i pokretanje `chat-api` servera
1. Otvorite terminal u folderu `projekti/dan7-finale/chat-api`.
2. Kreirajte `.env` fajl na osnovu `.env.example`.
3. Podesite parametre za LLM provider-a (Ollama ili DeepSeek) i obavezno postavite tačan URL za `db-api` server (npr. `DB_API_URL=http://127.0.0.1:8073`).
4. Kreirajte i aktivirajte virtualno okruženje, te instalirajte pakete:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
5. Pokrenite server na željenom portu (npr. **8074**):
   ```powershell
   uvicorn main:app --host 127.0.0.1 --port 8074 --reload
   ```

---

### Korak 4: Konfiguracija i pokretanje `frontend` klijenta
1. Otvorite fajl `projekti/dan7-finale/frontend/app.js` i provjerite da li `API_URL` pokazuje na pokrenuti port `chat-api` servera (npr. `http://127.0.0.1:8074/api/chat`).
2. Otvorite terminal u folderu `projekti/dan7-finale/frontend`.
3. Pokrenite jednostavni lokalni server (npr. na portu **8075**):
   ```powershell
   python -m http.server 8075
   ```
4. U pretraživaču otvorite adresu: [http://localhost:8075](http://localhost:8075) i počnite chat sa asistentom!
