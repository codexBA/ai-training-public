from typing import Any
import httpx 
import json
import os
from pathlib import Path
from dotenv import load_dotenv


# ovdje imeplementiramo funkcije koje ce model da koristi
# ove funkcije ce da pristupe nasem adresaru ne direktno citajuci json fajl vec pozivanje API (iz API foldera)
# koji ima mogucnost citanja podataka iz json fajla

# lookup_person
# list_people

# ova funkcija ce da vrati listu svih osoba iz json fajla
# koristi se za upite tipa: "koji su sve korisnici u sistemu?" 
# "nabroj sve korisnike" i slicno
def list_people() -> dict[str, Any]:
    url = "http://localhost:8020/osobe"

    with httpx.Client(timeout=5.0) as client:
        response = client.get(url)
        response.raise_for_status() # bacamo exception ako nije 200 OK
        return response.json()

# ova funkcija dohvata podatke o osobi preko adresara API-ja    
def lookup_person(name:str) -> dict[str, Any]:
    url = f"http://localhost:8020/osoba/{name.strip()}"

    with httpx.Client(timeout=5.0) as client:
        response = client.get(url)
        response.raise_for_status() # bacamo exception ako nije 200 OK
        return response.json()

# ova funkcija izvrsava tool/f-ju i vraca rezultat u string formatu koji ce LLM moci da koristi
def execute_tool(name: str, arguments: str) -> str:
    # pokusavamo parsirati arguments iz stringa u dict
    try:
        args_dict = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError:
        return f"Greska pri parsiranju argumenata: {arguments}"

    tool_functions = {
        "list_people": list_people,
        "lookup_person": lookup_person,
    }

    func = tool_functions.get(name)
    if not func:
        return f"Ne postoji funkcija {name}"
    
    try:
        if name == "list_people":
            result = func()
        elif name == "lookup_person":
            result = func(args_dict.get("name", ""))
        else:
            return f"Ne postoji funkcija {name}"
            
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Greska pri izvrsavanju funkcije {name}: {str(e)}"