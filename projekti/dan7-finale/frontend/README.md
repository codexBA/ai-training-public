# Frontend Client (Web)

Ovaj direktorij sadrži statički web klijent (Vanilla HTML/CSS/JS) za komunikaciju sa Chat API sistemom. Klijent je dizajniran u modernom "dark mode" stilu sa glassmorphism elementima, te pruža vizuelno privlačno iskustvo za korisnika.

## Pokretanje

Pošto se radi o čistom statičkom klijentu, možete ga pokrenuti na bilo koji način koji servira statične datoteke, npr:

### Opcija 1: VS Code Live Server
Otvorite `index.html` u VS Code editoru i pokrenite **Live Server** ekstenziju (desni klik -> Open with Live Server).

### Opcija 2: Python HTTP Server
U ovom direktoriju (`frontend`), pokrenite sljedeću komandu u terminalu:

```bash
python -m http.server 8080
```
Zatim otvorite preglednik i idite na [http://localhost:8080](http://localhost:8080).

## Povezivanje sa Backendom
Frontend očekuje da je **chat-api** server pokrenut na `http://127.0.0.1:8000`. Ukoliko ste mijenjali port u `chat-api`, morate ažurirati varijablu `API_URL` u `app.js` fajlu.
