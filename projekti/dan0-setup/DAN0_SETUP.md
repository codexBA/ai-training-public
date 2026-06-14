# Dan 0 — Priprema okruženja
## Šalje se polaznicima DAN PRIJE početka obuke

---

## Šta trebate instalirati (redoslijed je važan!)

### 1. Git

**Provjera:**
```bash
git --version
```
Očekivani output: `git version 2.x.x` (bilo koja 2.x verzija je ok)

**Download (ako nemate):** https://git-scm.com/download/win

**Konfiguracija nakon instalacije:**
```bash
git config --global user.name "Vaše Ime"
git config --global user.email "email@neka-domena.ba"
```

---

### 2. Python 3.11 / 3.12 / 3.13

> 💡 **ŠTA JE VIRTUALNO OKRUŽENJE (VENV)?**
> Prije nego što počnete sa radom na projektima u narednim danima, obavezno pročitajte naš brzi vodič: **[Zašto i kako koristiti Python venv](../../docs/venv-uputstvo.html)**. Ovo je najvažniji koncept za rad sa Pythonom koji će vas spasiti mnogih grešaka!

**Provjera:**
```bash
python --version
```
Očekivani output: `Python 3.11.x`, `Python 3.12.x` ili `Python 3.13.x`

**Download (ako nemate):** https://www.python.org/downloads/

**VAŽNO:** Označite **"Add Python to PATH"** pri instalaciji!

**NAPOMENA:** Verzije 3.11, 3.12 i 3.13 su sve kompatibilne s bibliotekama koje
koristimo na obuci. Ako već imate Python 3.x instaliran — nema potrebe za
reinstalacijom.

---

### 3. Visual Studio Code

**Provjera:** Pokrenite VS Code → Help → About (verzija 1.80+)

**Download:** https://code.visualstudio.com/download

**Ekstenzije (instalirajte unutar VS Code):**
- **Python** (Microsoft) — podrška za Python razvoj
- **Jupyter** (Microsoft) — omogućava otvaranje i pokretanje `.ipynb` (Jupyter Notebook) fajlova direktno u VS Code-u. Ovo su posebni fajlovi koji se koriste na edukaciji, a omogućavaju pisanje i izvršavanje koda dio po dio, uz tekstualna objašnjenja.

Kako instalirati ekstenzije:
1. Otvorite VS Code.
2. Na lijevoj strani ekrana kliknite na ikonicu sa kockicama ili pritisnite `Ctrl+Shift+X` (Extensions panel).
3. U polje za pretragu upišite "Python" → pronađite onaj čiji je autor Microsoft i kliknite "Install".
4. Zatim upišite "Jupyter" → pronađite onaj čiji je autor Microsoft i kliknite "Install".
---

### 4. Docker Desktop

> 💡 **NOVI STE U DOCKERU?**
> S obzirom da je Docker ključan za ovu edukaciju, pripremili smo detaljan i jednostavan vodič namijenjen početnicima. Toplo preporučujemo da pročitate: **[Detaljno Docker Uputstvo](../../docs/docker-uputstvo.html)** prije nego nastavite dalje!

**Provjera:**
```bash
docker --version
```
Očekivani output: `Docker version 24.x.x` ili novije

```bash
docker run hello-world
```
Očekivani output: `Hello from Docker!`

**Download:** https://www.docker.com/products/docker-desktop/

**VAŽNO:** Nakon instalacije:
1. Pokrenite Docker Desktop aplikaciju
2. Sačekajte dok se engine ne startuje (zelena ikona u system tray)
3. Tek tada `docker` komande rade u terminalu

**Napomena za Windows:** Docker Desktop zahtijeva WSL2 ili Hyper-V.
Ako vas installer pita — odaberite WSL2 (preporučeno).

---

### 5. ODBC Driver za SQL Server (17 ili 18)

**Provjera via PowerShell:**
```powershell
Get-OdbcDriver -Name "*SQL Server*" | Select-Object Name
```

**Tražite bilo koji od:**
- ODBC Driver 17 for SQL Server
- ODBC Driver 18 for SQL Server ← noviji, isto radi

**Ako driver NIJE na listi — instalirajte:**
```powershell
winget install Microsoft.ODBCDriverForSQLServer
```
ILI direktan download: https://go.microsoft.com/fwlink/?linkid=2249004

**NAPOMENA:** `pyodbc` biblioteka se instalira tek na Dan 6 — ovo je samo provjera
da je Windows ODBC driver prisutan na sistemu.

---

### 6. Finalna provjera — pokrenite ovu komandu

```bash
docker run hello-world
```
Trebate vidjeti: `Hello from Docker!`

Ako vidite tu poruku — **sve je spremno za Dan 1!**

---

## Testiranje kompletnog stack-a (5 minuta)

Nakon instalacije svega, pokrenite ovu provjeru:

```bash
# Klonirajte repozitorij (URL dobijate od predavača)
git clone <repo-url>
cd ai-trening

# Pokrenite infrastrukturne servise
docker-compose up -d sqlserver ollama chromadb

# Sačekajte ~30 sekundi, zatim provjerite:
docker ps
# Trebate vidjeti 3 running kontejnera:
#   ai-trening-sqlserver
#   ai-trening-ollama
#   ai-trening-chromadb
```

### Testiranje pojedinačnih servisa:

**SQL Server:**
```bash
docker exec -it ai-trening-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "Training123!" -C -Q "SELECT 'SQL Server radi' AS Status"
```
Očekivani output: `SQL Server radi`

**Ollama:**
```bash
curl http://localhost:11434/api/tags
```
Očekivani output: `{"models":[]}`

**ChromaDB:**
```bash
curl http://localhost:8000/api/v1/heartbeat
```
Očekivani output: `{"nanosecond heartbeat": ...}`

Ako sva tri servisa rade — **kompletni stack je spreman!**

---

## Ako nešto ne radi

### Problem: `python` komanda nije prepoznata
**Rješenje:** Reinstalirajte Python i obavezno uključite "Add Python to PATH".
Ili pokušajte s `python3` umjesto `python`.

### Problem: Docker Desktop ne startuje
**Rješenje:** Provjerite da je WSL2 instaliran:
```powershell
wsl --install
```
Restartujte računar nakon instalacije.

### Problem: `docker-compose` komanda ne radi
**Rješenje:** Novije verzije Docker Desktopa koriste `docker compose` (bez crtice):
```bash
docker compose up -d
```

### Problem: Port je već zauzet
**Rješenje:** Provjerite koji proces koristi port:
```powershell
netstat -ano | findstr :1433
```
Zatvorite proces koji koristi port ili promijenite port u docker-compose.yml.

---

**Kontakt:** Za pitanja i podršku obratite se predavaču — odgovorit ću do kraja dana.
