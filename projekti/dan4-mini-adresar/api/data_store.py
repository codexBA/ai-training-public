import json
from pathlib import Path

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
    