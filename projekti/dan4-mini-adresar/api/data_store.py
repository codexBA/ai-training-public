import json
from pathlib import Path
from typing import Any

DATA_PATH = Path("data/korisnici.json")

# ucitaj listu korisnika is json-a
def load_korisnici():    
    with open(DATA_PATH, "r", encoding="utf-8") as f: 
        data = json.load(f) 
    return data.get("korisnici", [])
 

def list_osobe():
    """Vrati formatiran string svih korisnika za AI """
    korisnici = load_korisnici()
    uprosteno_korisnici = [
        {            
            "ime": k["ime"],
            "prezime": k["puno_ime"],
            "grad": k["grad"]
        } for k in korisnici
    ]
    return {"osobe": uprosteno_korisnici, "ukupno": len(uprosteno_korisnici)}

# trazi osobu po imenu ili prezimenu ili punom imenu
def lookup_person(ime: str) -> dict[str, Any]:
    korisnici = load_korisnici()
    
    # varijabla koja ce sadrzavati one rezultate koji se poklapaju
    matches: list[dict[str, Any]] = []

    # pretvaramo ime koje korisnik trazi u malo slovo
    search_term = ime.lower()
    for k in korisnici:
        if (
            search_term in k.get("ime", "").lower() or
            search_term in k.get("prezime", "").lower() or
            search_term in k.get("puno_ime", "").lower()            
        ):
            matches.append(k)
    
    # ako nismo nista nasli vrati prazan rjecnik
    if not matches:
        return {
            "pronadjen":False,
            "greska":f"Osoba {ime} nije pronadjena u adresaru",
            "upit":ime
        } 

    osoba = matches[0]
    return{
        "pronadjen":True,
        "osobu":{            
            "puno_ime":osoba["puno_ime"],                        
            "posao":osoba["posao"],            
            "grad":osoba["grad"]
        }
    }