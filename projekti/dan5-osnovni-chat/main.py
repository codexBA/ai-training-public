# osnovni chat - najjednostavnij LLM klijent

import os # import operativnog sistema (za rad sa fajlovima)
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from zaposlenici import ZAPOSLENICI, gdje_radi

load_dotenv() # ucitavanje varijabli iz .env fajla

# kreiranje FastAPI aplikacije i ovo je glsavni objekat
# FastAPI je web framework koji nam omogucava da kreiramo API 
app = FastAPI(
    title="Osnovni Chat",
    description="Jednostavni chat sa LLM-om",
    version="0.0.1"
)

# funkcija koja kreira client za LLM
def get_llm_client():
    provider = os.getenv("LLMS_PROVIDER", "deepseek")

    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY nije definisan")

        client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        return client, "deepseek-chat"
    
    # ako je provider "ollama" onda kreiramo client za ollamu
    if provider == "ollama":
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
        client = AsyncOpenAI( base_url=f"{ollama_url}/v1", api_key="ollama")
        return client, model

    raise RuntimeError(f"Nepoznat provider: {provider}")
        
SYSTEM_PROMPT = (
    "Ti si nervozni asistent koji ne voli da radi ali ipak odgovori na pitanje." 
    "Za ono sto ne znas izmisli nesto ako ne znas." 
    "Za pitanja gdje neka osoba radi trebas pozvati funkciju gdje_radi. "    
    "Nikada nemoj reci da ne znas i da si izmislio podatak. Budi samouvjeren."
)

# lista alata koji ce biti dostupni LLM modelu
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "gdje_radi",
            "description": "vraca gdje radi zaposlenik. koristi za pitanja gdje radi neka osoba",
            "parameters": {
                "type": "object",
                "properties": {
                    "ime": {
                        "type": "string",
                        "description": "ime zaposlenika, npr. Denis, Ivana, Ajdin, Darko, Branislava, Anes, Mirsad, Belma"
                    }
                },
                "required": ["ime"]
            }
        }
    }
]

# asinhrona funkcija koja komunicira sa LLM
# chat sa tools - odredjuje da li ce se pozvati funkcija ili ne
async def pitaj_llm(poruka: str, temperature: float = 0.7) -> str:
    client, model = get_llm_client()

    messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": poruka}
        ]

    # ovim se salje zahtjev/pitanje modelu
    odgovor = await client.chat.completions.create(
        model=model, # model koji koristimo
        messages=messages,
        tools=TOOLS,
        tool_choice="auto", # model ce sam odluciti da li ce pozvati funkciju ili ne
        temperature=temperature, # temperature je parametar koji kontrolise kreativnost odgovora,sto veca temperatura to je odgovor kreativniji
        max_tokens=512 # maksimalan broj tokena koji ce model generisati
    )

    msg = odgovor.choices[0].message    

    # ako model ne zatrazi pozivanje funkcije, vrati odgovor
    if not msg.tool_calls:
        return msg.content or ""

    # ako model zatrazi pozivanje funkcije, pozovi je
    tc  = msg.tool_calls[0]
    # argumenti su u json formatu, treba ih konvertovati u python dictionary
    args = json.loads(tc.function.arguments)
    
    rezultat_funkcije = gdje_radi(args.get("ime",""))
    messages.append(msg.model_dump(exclude_none=True))
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tc.id,
            "content": rezultat_funkcije
        }
    )

    odgovor_2 = await client.chat.completions.create(
        model=model, 
        messages=messages,
        temperature=temperature,
        max_tokens=512
    )

    return odgovor_2.choices[0].message.content or ""

class ChatRequest(BaseModel):
    poruka: str = Field(..., description="Korisnicka poruka", min_length=1, max_length=1024)
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="kreativnost odgovora")

class ChatResponse(BaseModel):
    odgovor: str = Field(..., description="Odgovor modela")

@app.get('/')
async def root():
    return FileResponse('static/index.html') # kreira putanju do index.html

# prima korisnicku poruku i zaduzen je za komunikaciju sa LLM modelom i salje odgovor nazad korisniku
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(zahtjev: ChatRequest) -> ChatResponse:

    """endpoint koji prima poruku i vraca odgovor"""
    try:
        odgovor = await pitaj_llm(zahtjev.poruka, zahtjev.temperature)
        return ChatResponse(odgovor=odgovor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

