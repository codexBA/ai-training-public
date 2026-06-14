"""
Temperature Eksperiment — CLI aplikacija za ispitivanje temperature parametra.
Šalje isti prompt na API s različitim temperaturama i prikazuje razlike.
Zahtijeva DEEPSEEK_API_KEY u .env fajlu ili pokrenut Ollama server.

Pokretanje:
    python cli/temperature_cli.py

Autor: Erkan Islamovic | AI Trening
"""

import os
import time

# python-dotenv = čita .env fajl i postavlja environment varijable
from dotenv import load_dotenv
# openai = SDK za OpenAI-kompatibilne API-je (DeepSeek, Ollama, GPT)
from openai import OpenAI
# httpx = HTTP klijent za provjeru dostupnosti Ollama servera
import httpx

# Učitavamo .env iz parent foldera (projekti/dan1-tokeni/.env)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


def get_llm_client():
    """
    Vraća LLM klijent prema dostupnosti.
    Prioritet: DeepSeek API (cloud) → Ollama (lokalno)
    """
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    if deepseek_key and deepseek_key.startswith("sk-"):
        print("  Model: DeepSeek V3 (cloud)")
        return OpenAI(
            api_key=deepseek_key,
            base_url="https://api.deepseek.com"
        ), "deepseek-chat"

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        httpx.get(f"{ollama_url}/api/tags", timeout=2.0)
        model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
        print(f"  Model: Ollama lokalno ({model})")
        return OpenAI(
            api_key="ollama",
            base_url=f"{ollama_url}/v1"
        ), model
    except Exception:
        print("  GRESKA: Ni DeepSeek API ni Ollama nisu dostupni!")
        print("  Rjesenje A: Dodajte DEEPSEEK_API_KEY u .env fajl")
        print("  Rjesenje B: Pokrenite Ollama: docker compose up -d ollama")
        raise SystemExit(1)


def posalji_prompt(klijent, model, prompt, temperatura):
    """
    Šalje prompt na LLM API s zadanom temperaturom.
    Vraća tekst odgovora, broj tokena i trajanje.
    """
    pocetak = time.monotonic()

    odgovor = klijent.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                #"content": "Odgovaraj kratko, maksimalno 2-3 recenice. Bosanski jezik."
                "content": "Reply in English, maximum 2-3 sentences."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperatura,
        max_tokens=150
    )

    trajanje_ms = int((time.monotonic() - pocetak) * 1000)
    tekst = odgovor.choices[0].message.content or ""
    tokeni_in = odgovor.usage.prompt_tokens if odgovor.usage else 0
    tokeni_out = odgovor.usage.completion_tokens if odgovor.usage else 0

    return {
        "tekst": tekst.strip(),
        "tokeni_in": tokeni_in,
        "tokeni_out": tokeni_out,
        "trajanje_ms": trajanje_ms,
    }


def eksperiment_jedna_temperatura(klijent, model, prompt, temperatura, ponavljanja):
    """Pokreće isti prompt N puta s istom temperaturom."""
    print(f"\n{'='*60}")
    print(f"  Temperature = {temperatura} | Ponavljanja: {ponavljanja}")
    print(f"{'='*60}")

    ukupno_in = 0
    ukupno_out = 0

    for i in range(ponavljanja):
        rezultat = posalji_prompt(klijent, model, prompt, temperatura)
        ukupno_in += rezultat["tokeni_in"]
        ukupno_out += rezultat["tokeni_out"]

        print(f"\n  --- Pokusaj {i+1} (t={temperatura}) ---")
        print(f"  {rezultat['tekst']}")
        print(f"  [Tokeni: in={rezultat['tokeni_in']} out={rezultat['tokeni_out']} | "
              f"{rezultat['trajanje_ms']}ms]")

    # Cijena (DeepSeek V3)
    cijena = (ukupno_in / 1_000_000 * 0.14) + (ukupno_out / 1_000_000 * 0.28)
    print(f"\n  Ukupno: in={ukupno_in} out={ukupno_out} tokena | Cijena: ${cijena:.6f}")


def eksperiment_usporedba(klijent, model, prompt):
    """Pokreće isti prompt na tri temperature: 0.0, 0.7, 1.5."""
    print(f"\n{'='*60}")
    print(f"  POREĐENJE TEMPERATURA")
    print(f"  Prompt: \"{prompt}\"")
    print(f"{'='*60}")

    temperature = [0.0, 0.7, 1.5]
    for temp in temperature:
        rezultat = posalji_prompt(klijent, model, prompt, temp)
        print(f"\n  t={temp}: {rezultat['tekst']}")
        print(f"         [in={rezultat['tokeni_in']} out={rezultat['tokeni_out']} | "
              f"{rezultat['trajanje_ms']}ms]")

    print(f"\n  Primjetite: t=0.0 daje isti odgovor svaki put,")
    print(f"  dok t=1.5 daje razlicite, kreativnije varijacije.\n")


def main():
    """Glavna funkcija — interaktivni meni."""
    print("=" * 60)
    print("  TEMPERATURE EKSPERIMENT")
    print("  Ispitajte kako temperatura utjece na odgovore LLM-a")
    print("=" * 60)

    klijent, model = get_llm_client()

    print()
    print("  Komande:")
    print("    q                    — Izlaz")
    print("    uporedi              — Isti prompt na t=0.0, 0.7, 1.5")
    print("    <prompt>             — Unos prompta (slijedi odabir temperature)")
    print()

    while True:
        try:
            unos = input("Prompt: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDovidenja!")
            break

        if not unos:
            continue

        if unos.lower() == "q":
            print("Dovidenja!")
            break

        if unos.lower() == "uporedi":
            prompt = input("Unesite prompt za poređenje: ").strip()
            if prompt:
                eksperiment_usporedba(klijent, model, prompt)
            continue

        # Odabir temperature
        try:
            temp_unos = input("Temperatura (0.0-2.0) [0.7]: ").strip()
            temperatura = float(temp_unos) if temp_unos else 0.7
        except ValueError:
            temperatura = 0.7

        try:
            pon_unos = input("Broj ponavljanja [3]: ").strip()
            ponavljanja = int(pon_unos) if pon_unos else 3
        except ValueError:
            ponavljanja = 3

        ponavljanja = max(1, min(ponavljanja, 10))

        eksperiment_jedna_temperatura(klijent, model, unos, temperatura, ponavljanja)


if __name__ == "__main__":
    main()
