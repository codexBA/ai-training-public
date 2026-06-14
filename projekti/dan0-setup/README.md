# Dan 0 — Priprema okruženja

## Svrha

Ovaj "projekat" nije kod — to je **vodič za instalaciju** koji se šalje polaznicima
**dan prije početka obuke**. Cilj je da svi dođu na Dan 1 s potpuno funkcionalnim
razvojnim okruženjem, bez gubljenja vremena na instalacije tokom predavanja.

## Pedagoški cilj

Polaznik treba imati instalirano i testirano:
- Git (za preuzimanje materijala)
- Python 3.11+ (za pokretanje projekata)
- Docker Desktop (za kontejnerizaciju servisa)
- ODBC Driver za SQL Server (za Dan 6)

## Prerequisites

Ovo je **prvi korak** — nema prethodnih zahtjeva osim Windows računara s
administratorskim pravima za instalaciju softvera.

## Kako koristiti

1. Otvorite [DAN0_SETUP.md](DAN0_SETUP.md)
2. Pratite korake redom (slijed je važan!)
3. Na kraju pokrenite finalnu provjeru iz Koraka 6
4. Ako nešto ne radi — kontaktirajte predavača

## Struktura

```
dan0-setup/
├── README.md          ← Ovaj fajl
└── DAN0_SETUP.md      ← Korak-po-korak instalacijski vodič
```

## Česte greške i rješenja

| Problem | Rješenje |
|---------|----------|
| `python` komanda ne radi | Reinstalirajte Python s uključenom opcijom "Add Python to PATH" |
| Docker Desktop ne startuje | Provjerite da je Hyper-V / WSL2 omogućen u Windows Features |
| `docker run hello-world` javlja grešku | Pokrenite Docker Desktop i sačekajte zelenu ikonu (engine startup) |

## Kontakt

Za pitanja i podršku prije početka obuke obratite se predavaču: **Erkan Islamović**
