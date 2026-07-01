# Database API Server – .NET 10 verzija (`db-api-net10`)

> Ovo je **ASP.NET Core 10 Minimal API** alternativa originalnog Python/FastAPI `db-api` servisa.  
> Implementira identične endpointe, koristi isti SQL Server schema i radi na istom portu **8001**.

---

## Tehnički stack

| Python (`db-api`)     | .NET 10 (`db-api-net10`)         |
|-----------------------|----------------------------------|
| FastAPI               | ASP.NET Core Minimal API         |
| pyodbc                | Microsoft.Data.SqlClient 7.x     |
| Pydantic modeli       | C# `record` tipovi               |
| Uvicorn               | Kestrel (ugrađeni web server)    |
| `.env` fajl           | `appsettings.json`               |
| `python-dotenv`       | IConfiguration (ugrađeno)        |
| Swagger UI (/docs)    | Swagger UI (/swagger)            |

---

## Preduvjeti

1. **.NET 10 SDK** – preuzmite na [dotnet.microsoft.com](https://dotnet.microsoft.com/download/dotnet/10.0)
2. **SQL Server** s kreiranom bazom (`setup-database.sql` iz foldera `sqlskripte`)
3. **ODBC Driver 17** nije potreban – Microsoft.Data.SqlClient ima ugrađene drivere

---

## Konfiguracija

Otvorite `appsettings.json` i prilagodite postavke baze:

```json
// Opcija 1: Windows Authentication (Trusted Connection)
"DB_SERVER": "localhost\\SQLEXPRESS",
"DB_NAME": "StateStatisticsDB",
"DB_TRUSTED_CONNECTION": "yes"

// Opcija 2: SQL Server Authentication
"DB_TRUSTED_CONNECTION": "no",
"DB_USER": "tvoj_korisnik",
"DB_PASSWORD": "tvoja_lozinka"
```

> **Napomena:** Alternativno možete postaviti puni `ConnectionStrings:DefaultConnection` string u `appsettings.json` (vidi komentar u fajlu).

---

## Pokretanje

```bash
# Iz foldera db-api-net10:
dotnet run
```

Server će se pokrenuti na:
- **HTTP**:  `http://localhost:8001`
- **Swagger UI**: `http://localhost:8001/swagger`

Za development s hot-reload:
```bash
dotnet watch run
```

---

## API Endpointi

Identični Python/FastAPI verziji:

| Metoda | Putanja                          | Opis                                         |
|--------|----------------------------------|----------------------------------------------|
| GET    | `/api/departments`               | Sva odjeljenja/ministarstva                  |
| GET    | `/api/employees`                 | Svi zaposlenici                              |
| GET    | `/api/employees/search?name=...` | Pretraga zaposlenika po imenu/prezimenu      |
| GET    | `/api/economic-data?year=2023`   | Ekonomski podaci po regijama za datu godinu  |
| GET    | `/api/projects/budget?department_code=MF` | Ukupan budžet projekata odjeljenja |

---

## Razlike u odnosu na Python verziju

- **Async by default** – svi endpointi koriste `async/await` i asinhroni SQL čitač
- **Bez ODBC drivera** – `Microsoft.Data.SqlClient` uključuje native drivere
- **Tipizirani modeli** – C# `record` tipovi pružaju compile-time sigurnost umjesto Pydantic runtime validacije
- **Konfiguracija** – `appsettings.json` umjesto `.env` fajla; podržava i Environment Variables direktno
- **Port**: Server radi na `8001` (isti port kao Python verzija)
