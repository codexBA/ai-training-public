
import os # import operativnog sistema (za rad sa fajlovima)

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from dokument import ucitaj_dokument, podijeli_na_dijelove
from pretraga import pronadji_relevantne

load_dotenv() # ucitava varijable iz .env fajla

TOP_K = 3

SYSTEM_PROMPT = (
    "Ti si asistent koji odgovara na pitanja na osnovu datog konteksta."
    "Kontekst se sastoji od dijelova dokumenta koji su relevantni za pitanje."
    "Ako odgovor nije moguc na osnovu datog konteksta, reci da ne znas."
    "Ne izmisljaj odgovore."    
)

DIJELOVI = podijeli_na_dijelove(ucitaj_dokument())  

app = FastAPI(
    title="RAG Chat",
    description="Jednostavni RAG chat sa LLM-om",
    version="0.0.1"
)

# definisemo funkciju koja ce kreirati client za LLM model
def get_llm_client():
    provider = os.getenv("LLMS_PROVIDER", "deepseek")
    
    if provider == "deepseek":
        api_key =  os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY nije definisan")
        # kreiraj client za OpenAI
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        return client, "deepseek-chat"

    # ako je provider "ollama" onda kreiramo client za ollamu
    if provider == "ollama":
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
        client = AsyncOpenAI(base_url=f"{ollama_url}/v1", api_key="ollama")
        return client, model
    
    raise RuntimeError(f"Nepoznat provider: {provider}")



# ovo je kompleksna funkcija koja poziva funkciju pronadji_relevantne iz pretraga.py fajla
# i koristi kontekst koji vrati ta funkcija da bi odgovorila na pitanje
async def pitaj_rag(pitanje: str, temperature: float = 0.7) -> tuple[str, list[dict]]:
    pronadjeni = pronadji_relevantne(pitanje, DIJELOVI, TOP_K)

    if pronadjeni:
        kontekst = "\n\n---\n\n".join(p["tekst"] for p in pronadjeni)
        user_sadrzaj = f"KONTEKST:\n\n {kontekst}\n\nPITANJE:{pitanje}"
    else:
        user_sadrzaj = f"KONTEKST:\n\n nema pronadjenih odlomaka\n\nPITANJE:{pitanje}"
    
    client, model = get_llm_client()

    odgovor = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_sadrzaj}
        ],
        temperature=temperature,
        max_tokens=1024
    )

    # uzimamo odgovor od LLM-a
    llm_odgovor = odgovor.choices[0].message.content or ""

    # vracamo odgovor LLM-a i pronadjene odlomke
    return llm_odgovor, pronadjeni

# ovo se salje kao zahtjev prema chat endpointu
class ChatRequest(BaseModel):
    poruka: str = Field(min_length=1)
    temperatura: float = Field(default=0.3, ge=0.0, le=1.5)

# ovo se vraca kao odgovor iz chat endpointa
class ChatResponse(BaseModel):
    odgovor: str
    pronadeni_dijelovi: list[dict]

@app.get("/")
def index():
    return FileResponse("static/index.html")

# kreiramo endpoint za pretragu i to samo keyword pretraga tekstualnog dokumenta
@app.get("/api/pretraga")
async def pretraga(q: str = Query(..., description="Pitanje koje zelite da postavite"), ):
    pronadjeni = pronadji_relevantne(q, DIJELOVI, TOP_K)
    return {"pronadeni_dijelovi": pronadjeni, "upit": q}

#kreiramo endpoint za chat - on koristi funkciju pitaj_rag da bi odgovorila na pitanje
@app.post("/api/chat")
async def chat(zahtjev: ChatRequest):
    odgovor, pronadeni = await pitaj_rag(zahtjev.poruka, zahtjev.temperatura)
    return ChatResponse(odgovor=odgovor, pronadeni_dijelovi=pronadeni)
        
    

    
    