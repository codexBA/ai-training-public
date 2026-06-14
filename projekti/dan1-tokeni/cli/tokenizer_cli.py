"""
Token Analizator — CLI aplikacija za analizu tokenizacije teksta.
Koristi tiktoken biblioteku za precizno brojanje tokena.
Ne zahtijeva API key — radi potpuno offline.

Pokretanje:
    python cli/tokenizer_cli.py

Autor: Erkan Islamovic | AI Trening
"""

# tiktoken = OpenAI biblioteka za preciznu tokenizaciju
# Ista biblioteka koju koriste GPT-4, DeepSeek i drugi modeli
import tiktoken


def inicijaliziraj_enkoder():
    """
    Kreira tiktoken enkoder za cl100k_base encoding.
    cl100k_base je encoding koji koriste GPT-4 i DeepSeek modeli.
    """
    return tiktoken.get_encoding("cl100k_base")


def analiziraj_tekst(tekst, enkoder):
    """
    Analizira tekst i vraća detaljne informacije o tokenima.

    Parametri:
        tekst   - tekst za analizu
        enkoder - tiktoken enkoder

    Vraća:
        dict sa svim informacijama o tokenima
    """
    # Enkodiranje teksta u listu token ID-ova
    token_ids = enkoder.encode(tekst)
    # Dekodiranje svakog tokena nazad u tekst
    tokeni_tekst = [enkoder.decode([tid]) for tid in token_ids]

    # DeepSeek V3 cijene (juni 2025)
    cijena_input_per_1m = 0.14  # $0.14 po milion input tokena
    cijena_output_per_1m = 0.28  # $0.28 po milion output tokena

    broj_tokena = len(token_ids)
    broj_znakova = len(tekst)
    omjer = broj_znakova / broj_tokena if broj_tokena > 0 else 0

    # Procjena cijene za jedan API poziv (samo input)
    cijena_jedan_poziv = broj_tokena / 1_000_000 * cijena_input_per_1m
    # Procjena za 1000 poziva
    cijena_1000_poziva = cijena_jedan_poziv * 1000

    return {
        "tekst": tekst,
        "broj_tokena": broj_tokena,
        "broj_znakova": broj_znakova,
        "omjer_znakova_po_tokenu": round(omjer, 2),
        "tokeni": tokeni_tekst,
        "token_ids": token_ids,
        "cijena_jedan_poziv": cijena_jedan_poziv,
        "cijena_1000_poziva": cijena_1000_poziva,
    }


def prikazi_rezultat(rezultat):
    """Prikazuje rezultat analize u čitljivom formatu."""
    print(f"\n{'='*60}")
    print(f"  Tekst:    \"{rezultat['tekst']}\"")
    print(f"  Znakovi:  {rezultat['broj_znakova']}")
    print(f"  Tokeni:   {rezultat['broj_tokena']}")
    print(f"  Omjer:    {rezultat['omjer_znakova_po_tokenu']} znakova/token")
    print(f"{'='*60}")

    # Prikaz pojedinačnih tokena s bojama (ASCII)
    print("\n  Token lista:")
    for i, (tok, tid) in enumerate(
        zip(rezultat["tokeni"], rezultat["token_ids"])
    ):
        prikaz = repr(tok)
        print(f"    [{i+1:2d}] {prikaz:<20s}  (ID: {tid})")

    # Prikaz cijene
    print(f"\n  Procijenjena cijena (DeepSeek V3 input):")
    print(f"    Jedan poziv:  ${rezultat['cijena_jedan_poziv']:.7f}")
    print(f"    1000 poziva:  ${rezultat['cijena_1000_poziva']:.4f}")
    print()


def uporedi_jezike(enkoder):
    """Upoređuje tokenizaciju istog sadržaja na bosanskom i engleskom."""
    parovi = [
        ("Sarajevo je glavni grad Bosne i Hercegovine.",
         "Sarajevo is the capital city of Bosnia and Herzegovina."),
        ("Dobro jutro, kako ste danas?",
         "Good morning, how are you today?"),
        ("Ministarstvo finansija objavljuje godišnji izvještaj.",
         "The Ministry of Finance publishes the annual report."),
    ]

    print(f"\n{'='*60}")
    print("  POREĐENJE: Bosanski vs Engleski")  
    print(f"{'='*60}")
    print(f"  {'Tekst':<45s} {'BS':>4s} {'EN':>4s} {'Razlika':>8s}")
    print(f"  {'-'*45} {'----':>4s} {'----':>4s} {'--------':>8s}")

    for bs, en in parovi:
        tok_bs = len(enkoder.encode(bs))
        tok_en = len(enkoder.encode(en))
        razlika = tok_bs - tok_en
        predznak = "+" if razlika > 0 else ""
        # Skraćeni tekst za prikaz
        kratki = bs[:42] + "..." if len(bs) > 45 else bs
        print(f"  {kratki:<45s} {tok_bs:>4d} {tok_en:>4d} {predznak}{razlika:>7d}")

    print(f"\n  Zaključak: Bosanski tekst troši ~1.5-2x više tokena od engleskog.")
    print(f"  To znači veće troškove API poziva za sadržaj na bosanskom jeziku.\n")


def main():
    """Glavna funkcija — interaktivna petlja za unos teksta."""
    print("=" * 60)
    print("  TOKEN ANALIZATOR")
    print("  Precizna tokenizacija s tiktoken bibliotekom")
    print("  Encoding: cl100k_base (GPT-4, DeepSeek)")
    print("=" * 60)
    print()
    print("  Komande:")
    print("    q         — Izlaz iz programa")
    print("    uporedi   — Poređenje bosanskog i engleskog")
    print("    <tekst>   — Analiziraj uneseni tekst")
    print()

    enkoder = inicijaliziraj_enkoder()

    while True:
        try:
            unos = input("Unesite tekst: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDoviđenja!")
            break

        if not unos:
            continue

        if unos.lower() == "q":
            print("Doviđenja!")
            break

        if unos.lower() == "uporedi":
            uporedi_jezike(enkoder)
            continue

        rezultat = analiziraj_tekst(unos, enkoder)
        prikazi_rezultat(rezultat)


if __name__ == "__main__":
    main()
