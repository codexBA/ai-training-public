ZAPOSLENICI = {
    "Denis": "Vlada",
    "Ajdin": "Hotel",
    "Ivana": "Ministartvo pravde",
    "Darko": "Fakultet Informacionih Nauka",
    "Branislava": "Agencija za Statistiku",
    "Anes": "VSTV",
    "Mirsad": "Ured za Harmnizaciju",
    "Belma": "Služba za Zaposljavanje"    
}


# ova funkcija pretrazuje rjecnik i vraca vrijednost ako nadje kljuc
# ako ne nadje kljuc vraca "Ne znam gdje radi"
def gdje_radi(ime: str) -> str:
    """Vraca gdje radi osoba"""
    if not ime:
        return "Moras navesti ime osobe"

    ime = ime.strip().lower() 
    for osoba, firma in ZAPOSLENICI.items():
        if osoba.lower() == ime:
            return f"{osoba} radi u {firma}"
    return "Ne znam gdje radi"
    