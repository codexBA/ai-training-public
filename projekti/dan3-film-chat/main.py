import json # rad sa json fajlovima 
import random # rad sa random brojevima  - za nasumicni izbor iz liste

from pathlib import Path # rad sa putanjama do fajlova 
from fastapi import FastAPI # web framework - kreira API endpointe
from fastapi.staticfiles import StaticFiles # omogucuje serviranje statickih fajlova 
from fastapi.responses import FileResponse # omogucava vracanje fajlova kao odgovor - za index.html
from pydantic import BaseModel, Field # za kreiranje modela podataka 
from typing import List, Optional, Literal
import os # rad sa operativnim sistemom
from dotenv import load_dotenv # ucitavanje varijabli iz .env fajla 
from openai import AsyncOpenAI # OpenAI SDK - radi i s DeepSeek i Ollama API-jem

load_dotenv() # ucitavanje varijabli iz .env fajla 

# kreiranje FastAPI aplikacije 
app = FastAPI(title="Film Chat API", description="API za Film Chat", version="1.0.0") 
# servisiranje statickih fajlova 
app.mount("/static", StaticFiles(directory="static"), name="static") 

# kreiranje LLM klijenta - DeepSeek ili Ollama
def get_llm_client():
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if api_key and api_key.startswith("sk-"):
        return AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1"), "deepseek-v4-flash"
    
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
    return AsyncOpenAI(base_url=f"{ollama_url}/v1", api_key="ollama"), model


# definisanje putanje do filmovi.json fajla 
FILMOVI_PATH = Path(__file__).parent / "filmovi.json"

# ucitavanje filmova iz JSON fajla 
def ucitaj_filmove() -> list:
    """Ucitava filmove iz JSON fajla."""
    with open(FILMOVI_PATH, encoding="utf-8") as f:
        return json.load(f)

# kreiranje modela za API poruke
class Poruka(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    poruke: List[Poruka]
    system_prompt: Optional[str] = None
    max_tokens: int = 500 
  
class ChatResponse(BaseModel):
    odgovor: str
    poruke: List[Poruka]
        
class PreporukaRequest(BaseModel):
    zanr: Optional[str] = None
    raspolozenje: str = "opusteno"    

class PreporukaResponse(BaseModel):
    film_id: int
    naslov: str
    razlog: str
    ocjena_poklapanja: float # ocjena izmedju 1 i 10

DEFAULT_SYSTEM = """Ti si asistent za preopruku filmova. 
Koristi SAMO filmove iz dostavljenog JSON kataloga. 
Ako film nije u katalogu ti reci da ne znas. Budi koncizan i duhovit. Maksimalno 4 recenice"""

# lista svih zanrova iz JSON fajla


def filmovi_u_kontekst(filmovi: list, limit: int = 50) -> str:
    skraceno = [
        {
            "id": film["id"],
            "naslov": film["naslov"],
            "zanr": film["zanr"],
            "ocjena": film["ocjena"]            
        }
        for film in filmovi[:limit]
    ]
    
    return json.dumps(skraceno)

   
# ruta - HTTP metod - GET - dohvat podatak - otvara pocetnu stranicu / 
@app.get("/") 
async def read_index(): 
    # vraca index.html fajl - kreiran u folderu static
    return FileResponse('static/index.html') 
    #return {"poruka": "API je aktivan"}

@app.get("/api/filmovi")
async def lista_filmova():
    filmovi = ucitaj_filmove()
    return {"filmovi": filmovi, "ukupno": len(filmovi)}
    

@app.get("/api/filmovi/{film_id}")
async def detalji_filma(film_id: int):
    filmovi = ucitaj_filmove()
    for film in filmovi:
        if film["id"] == film_id:
            return film
    return {"error": "Film nije pronadjen"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(zahtjev: ChatRequest):
    # chat sa punom historijom pruka, mi saljemo cijeli niz poruka
    klijent, model = get_llm_client()
    filmovi = ucitaj_filmove()
    
    # provjera sistemske poruke - ako nije poslana koristi default
    system = zahtjev.system_prompt or DEFAULT_SYSTEM
    system += "\n\n" + "Katalog filmova: " + filmovi_u_kontekst(filmovi, 50)

    poruke_api = [{"role": "system", "content": system}]
    # kopiramo historiju message
    for poruka in zahtjev.poruke:
        if poruka.role != "system":
            poruke_api.append({
                "role": poruka.role,
                "content": poruka.content
            })
    
    odgovor_llm = await klijent.chat.completions.create(
        model=model,
        temperature=0.7,
        messages=poruke_api,
        max_tokens = 500
    )

    tekst_odgovora = odgovor_llm.choices[0].message.content
    nova_historija = list(zahtjev.poruke) + [Poruka(role="assistant", content=tekst_odgovora)]
    

    return  ChatResponse(
        odgovor = tekst_odgovora,
        poruke = nova_historija
    )


@app.post("/api/preporuci", response_model=PreporukaResponse)
async def preporuci_film(zahtjev: PreporukaRequest):
    """Strukturirani JSON output — za automatizaciju."""
    klijent, model = get_llm_client()
    filmovi = ucitaj_filmove()

    prompt = f"""Odaberi jedan film iz kataloga za korisnika.
Žanr (opciono): {zahtjev.zanr or 'bilo koji'}
Raspoloženje: {zahtjev.raspolozenje}
Max trajanje (min): {zahtjev.max_trajanje_min or 'bez limita'}

Katalog: {filmovi_u_kontekst(filmovi, limit=40)}

Vrati ISKLJUČIVO validan JSON s poljima:
{{"film_id": number, "naslov": "string", "razlog": "string", "ocjena_poklapanja": 1-10}}"""

    odgovor = await klijent.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Ti vraćaš samo JSON, bez markdowna."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=300,
        response_format={"type": "json_object"},
    )
    sadrzaj = odgovor.choices[0].message.content or "{}"
    podaci = json.loads(sadrzaj)
    return PreporukaResponse(**podaci)

    
    