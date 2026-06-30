# jednostavna keyword pretraga - bez embeddinga i vektorske baze
# koristi se samo string pretraga i sortira se po relevantnosti
# Relevantnost se izracunava na osnovu broja pojavljivanja kljucnih rijeci

import re # Regularni izrazi za pretragu ključnih riječi

# Set riječi (stop words) koje su vrlo česte i ne nose specifično značenje.
# Ignorišemo ih kako ne bismo dodjeljivali bodove za poklapanja na veznicima i prijedlozima.
STOP_WORDS = {
    "i", "je", "u", "sa", "za", "na", "se", "kao", "da", "od", 
    "do", "od", "po", "koji", "koja", "koje", "sve", "sam", "si", "smo", "ste", "su"
}


# pretvara tekst u set unikatnih rijeci - sa filtriranjem stop_words i sva slova se pretvaraju u mala slova
# regex uklanja interpunkciju i brojeve
def ocisti_tekst(tekst: str) -> set[str]:
    """Obrisi tekst i vrati set rijeci"""
    
    # regex koji uzima riječi sa slovima bosanskog jezika i konvertuje ih u mala slova
    rijeci = re.findall(r'[a-zA-ZČčĐđŽžŠšĆć]+', tekst.lower()) 

    # ovdje radimo filtering rijeci koristeći set comprehension - izbacujemo stop_words i kraće od 3 slova
    return {r for r in rijeci if r not in STOP_WORDS and len(r) >= 3}
    
# funkcija bodovanja
def izracunaj_bod(pitanje: str, odlomak: str) -> int:
    """Izracunaj broj bodova - koliko zajednickih rijeci pitanje dijeli sa odlomkom"""

    rijeci_pitanja = ocisti_tekst(pitanje)
    rijeci_odlomka = ocisti_tekst(odlomak)

    # broj zajednickih rijeci
    return len(rijeci_pitanja & rijeci_odlomka)


# pretrazuje sve dijelove dokumenta i vraca top_k najrelevantinijih za postavljeno pitanje na osnovu broja
# zajednickih rijeci 
# R - Retrieval (nalazenje relevantnog konteksta)
def pronadji_relevantne(pitanje: str, dijelovi: list[str], top_k: int = 2) -> list[dict]:
    rezultati = []

    for odlomak in dijelovi:
        # bodovanje 
        bod = izracunaj_bod(pitanje, odlomak)

        if bod > 0:
            rezultati.append({"tekst": odlomak, "bod": bod})
    
    # sortiramo rezultate od najveceg broja zajednickih rijeci prema najmanjem
    rezultati.sort(key=lambda x: x["bod"], reverse=True)
    
    # vracamo top k relevantnih dijelova
    return rezultati[:top_k]
