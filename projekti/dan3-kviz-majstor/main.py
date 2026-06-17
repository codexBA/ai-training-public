import json # rad sa json fajlovima 
import random # rad sa random brojevima  - za nasumicni izbor iz liste

from pathlib import Path # rad sa putanjama do fajlova 
from fastapi import FastAPI # web framework - kreira API endpointe
from fastapi.staticfiles import StaticFiles # omogucuje serviranje statickih fajlova 
from fastapi.responses import FileResponse # omogucava vracanje fajlova kao odgovor - za index.html
from pydantic import BaseModel, Field # za kreiranje modela podataka 

import os # rad sa operativnim sistemom
from dotenv import load_dotenv # ucitavanje varijabli iz .env fajla 
from openai import AsyncOpenAI # OpenAI SDK - radi i s DeepSeek i Ollama API-jem

# ucita varijable iz .env fajla 
load_dotenv() 

app = FastAPI(
    title="Dan3 - Kviz Majstor",
    description="Treći dan AI obuke - Kviz Majstor",
    version="0.0.1"
)

#Servira HTML/CSS/JS fajlove iz "static" foldera
app.mount("/static", StaticFiles(directory="static"), name="static")

# definisanje llm klijenta koji ce raditi i sa DeepSeek i sa Ollama API-jem
def get_llm_client():
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if api_key and api_key.startswith("sk-"):
        return AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1"), "deepseek-v4-flash"
    
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
    return AsyncOpenAI(base_url=f"{ollama_url}/v1", api_key="ollama"), model

# 1 - citanje iz json-a
KVIZ_PATH = Path(__file__).parent / "kviz.json"
with open(KVIZ_PATH, encoding="utf-8") as f:
    PITANJA = json.load(f)

# klase za API enpointe
# 1 - endpoint za slanje upita prema API
class OdgovorRequest(BaseModel):
    pitanje_id: int 
    odgovor_studenta: str

# 2 - odgovor koji vraca API
class OcjenaResponse(BaseModel):
    tacno: bool
    bodovi: int 
    komentar: str
    tacan_odgovor: str

# varijabla koja cuva postavljena pitanja
postavljena_pitanja: dict[int, dict] = {}

@app.get("/")
async def root():
    return FileResponse("static/index.html")
    #return {"poruka": "Dobro dosao u kviz majstor"}

# endpoint koji vraca kategoriej pitanje
@app.get("/api/kategorije")
async def get_kategorije():
    return list({p["kategorija"] for p in PITANJA})

# endpoint koji vraca random pitanje
@app.get("/api/pitanje")
async def daj_pitanje():
    pitanje = random.choice(PITANJA)
    postavljena_pitanja[pitanje["id"]] = pitanje
    
    return {
        "id" : pitanje["id"],
        "kategorija": pitanje["kategorija"],
        "pitanje": pitanje["pitanje"],
        "tezina": pitanje["tezina"]        
    }

# ovaj endpoint prima odgovor studenta (OdgovorRequest) i vraca ocjenu (OcjenaResponse)
@app.post("/api/provjeri", response_model=OcjenaResponse)
async def provjeri(req: OdgovorRequest):
    # provjeravamo da li pitanje koje se odgovara postoji u kolekciji postavljenih pitanja
    pitanje_data = postavljena_pitanja.pop(req.pitanje_id, None)

    if not pitanje_data:
        return OcjenaResponse(
            tacno=False,
            bodovi=0,
            komentar="Pitanje nije pronadjeno. Pokusajte ponovo",
            tacan_odgovor=""
        )
    # kreiramo sistemski prompt za kviz-sudiju. Ovim definisemo kako ce se model ponasati 
    system_prompt = (
        "Ti si kviz-sudija. Uporedi odgovor studenta sa tacnim odgovorom.\n"
        "Prihvati sinonime i slicne odogvore a zanemari gratmaticke greske u pisanju.\n\n"
        "Obrazlozi i komentarisi odgovor bez obzira bio tacan ili ne. Prosiri svoj komentar sa informacijama koje su vezane za pitanje i koje su zanimljive. \n\n"
        "Budi grub i nepristojan ako odgovor nije tacan. Ako je tacan, uvijek izrazi sumnju u odgovor i reci da je to vjerovatno tacan odgovor ali budi sarkastican. \n\n"
        "Ogranici odgovor na 3 - 4 recenice.  \n\n"
        f"Pitanje: {pitanje_data['pitanje']}\n"
        f"Tacan odgovor: {pitanje_data['tacan_odgovor']}\n"
        f"Odgovor studenta: {req.odgovor_studenta}"
        "Vrati odgovor u JSON formatu sa kljucevima: 'tacno' (bool), 'bodovi' (1-10), 'komentar' (str), 'tacan_odgovor' (str)"
    )

    # kontaktiramo LLM sa pitanjem i odgovoroom i trazimo da ocjeni tacnost/ispravnost odgovora
    client, model = get_llm_client()

    # odgovor LLM-a
    response = await client.chat.completions.create(
        model=model,
        temperature=0.0,
        messages=[
            {"role":"system", "content": system_prompt},
            {"role": "user", "content": "Ocijeni odgovor studenta."}
        ]
    )
    
    # formatiramo odgovor LLM-a i pretvaramo ga u JSON
    raw = response.choices[0].message.content.strip()    
    rezultat = json.loads(raw)

    return OcjenaResponse(
        tacno=rezultat["tacno"],
        bodovi=rezultat["bodovi"],
        komentar=rezultat["komentar"],
        tacan_odgovor=rezultat["tacan_odgovor"]
    )
    
