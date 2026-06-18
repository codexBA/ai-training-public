from tools.adresar import execute_tool

import json
import os
from pathlib import Path 

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

from dotenv import load_dotenv
from typing import List, Dict, Any

_PROJECT_ROOT = Path(__file__).parent.parent
# ucitavanje .env fajla 
load_dotenv(dotenv_path=_PROJECT_ROOT / ".env") 

# definisanje llm klijenta koji ce raditi i sa DeepSeek i sa Ollama API-jem
def get_llm_client():
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if api_key and api_key.startswith("sk-"):
        return AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1"), "deepseek-v4-flash"
    
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
    return AsyncOpenAI(base_url=f"{ollama_url}/v1", api_key="ollama"), model

class AskRequest(BaseModel):
    pitanje: str
    tool_choice: str = "auto"

class AskResponse(BaseModel):
    pitanje: str
    odgovor: str
    model: str
    trajanje_ms: int

# kreiranje FastAPI aplikacije 
app = FastAPI(
    title="Dan4 - Mini Adresar",
    description="Cetvrti dan AI obuke - Mini Adresar",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")
    #return {"poruka": "Dobro dosao u Mini Adresar"}

@app.post("/api/ask", response_model=AskResponse)
async def ask(zahtjev: AskRequest):
    klijent, model = get_llm_client()

    messages=[
        {"role":"system","content":system_prompt},
        {"role":"user","content":zahtjev.pitanje}
    ]

    odgovor = await run_llm(klijent, model, messages)

    return AskResponse(
        pitanje=zahtjev.pitanje,
        odgovor=odgovor,
        model=model,
        trajanje_ms=0
    )
    

async def run_llm(
    klijent: AsyncOpenAI,
    model: str,
    messages: list,    
)->str:
    current_messages = list(messages)
    max_tool_calls = 5
    
    for _ in range(max_tool_calls):
        response = await klijent.chat.completions.create(
            model=model,
            temperature=0.0,
            messages=current_messages,
            tools=TOOLS,
            tool_choice="auto"        
        )

        msg = response.choices[0].message
        # provjeravamo da li je LLM koristion tools
        if not msg.tool_calls:
            return msg.content

        current_messages.append(msg.model_dump(exclude_none=True))

        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = tc.function.arguments or {}

            result_str = execute_tool(fn_name, fn_args)
            
            current_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,                
                    "content": result_str
                }
            )

    return "Maximalan broj poziva alata je porekoracen"







# kreiramo sistemki prompt kojim definisemo ponasanje modela
system_prompt = """
Ti si asistent koji odgovara na pitanja o tome gdje ljudi rade i žive.
Za činjenice MORAŠ koristiti alate lookup_person i list_people ne smijes nista izmisljati. 
Kada korisnik pita "gdje radi" - koristi posao i ustanovu iz alata.
Kada pita "gdje živi" ili "u kom gradu" - koristi grad iz alata.
"""

# ovdje ćemo definisati alate - model čita opise alata i odlučuje koji će i kada koristiti

TOOLS=[    
    {
        "type":"function",
        "function":{
            "name":"lookup_person",
            "description": (
                "Dohvata podatke o osobi iz adresara (posao, ustanova, grad)."            
                "Koristi kada korisnik pita gdje neko radi, gdje zivi ili slicna pitanja koja se odnose na jednu osobu."
            ),
            "parameters":{
                "type":"object",
                "properties":{
                    "name":{
                        "type":"string",
                        "description":"Ime ili puno ime osobe, npr. Mirsad Ribic"
                    },
                },
                "required":["name"]
            },
        },
    },
    {
        "type":"function",
        "function":{
            "name":"list_people",
            "description":(
                "Vraća listu svih osoba iz adresara."
                "Koristi kada korisnik pita za listu svih osoba ili kada treba provjeriti spisak osoba ili kada korisnik pita koga poznaješ."
            ),
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[]
            },
        },
    },
]
    