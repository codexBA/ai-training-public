import os
import json
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="LLM Chat API",
    description="API za komunikaciju sa LLM i pristup bazi putem alata",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_API_URL = os.getenv("DB_API_URL", "http://127.0.0.1:8001")

def get_llm_client():
    provider = os.getenv("LLMS_PROVIDER", "deepseek")
    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY nije definisan")
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        return client, "deepseek-chat"
    
    if provider == "ollama":
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
        client = AsyncOpenAI(base_url=f"{ollama_url}/v1", api_key="ollama")
        return client, model

    raise RuntimeError(f"Nepoznat provider: {provider}")

SYSTEM_PROMPT = (
    "Ti si koristan asistent zadužen za analizu državne statistike. "
    "Kada te korisnik pita za podatke (poput odjeljenja, zaposlenika, budžeta, ekonomskih podataka), OBAVEZNO koristi dostupne funkcije da dohvatiš tačne informacije. "
    "Nemoj izmišljati podatke. Odgovori strukturirano i jasno na osnovu podataka iz funkcija."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_departments",
            "description": "Vraća listu svih državnih odjeljenja (ministarstava, agencija) i njihov kod",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_employees",
            "description": "Vraća listu svih zaposlenika i njihove pozicije",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_employees",
            "description": "Pretražuje zaposlenika po imenu ili prezimenu kako bi se našlo gdje rade i koja im je pozicija",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Ime ili prezime zaposlenika"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_economic_data",
            "description": "Dohvaća ekonomske podatke (BDP, nezaposlenost, plate) po regijama za određenu godinu",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "Godina za koju se traže podaci, npr. 2023 ili 2024"
                    }
                },
                "required": ["year"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_budget",
            "description": "Vraća ukupan budžet svih projekata za određeno odjeljenje",
            "parameters": {
                "type": "object",
                "properties": {
                    "department_code": {
                        "type": "string",
                        "description": "Skraćenica (kod) odjeljenja, npr. 'MF', 'MO', 'MZ'"
                    }
                },
                "required": ["department_code"]
            }
        }
    }
]

async def execute_tool(tool_name: str, args: dict) -> str:
    try:
        async with httpx.AsyncClient() as client:
            if tool_name == "get_departments":
                response = await client.get(f"{DB_API_URL}/api/departments")
            elif tool_name == "get_all_employees":
                response = await client.get(f"{DB_API_URL}/api/employees")
            elif tool_name == "search_employees":
                response = await client.get(f"{DB_API_URL}/api/employees/search", params={"name": args.get("name", "")})
            elif tool_name == "get_economic_data":
                response = await client.get(f"{DB_API_URL}/api/economic-data", params={"year": args.get("year", 2023)})
            elif tool_name == "get_project_budget":
                response = await client.get(f"{DB_API_URL}/api/projects/budget", params={"department_code": args.get("department_code", "")})
            else:
                return f"Nepoznata funkcija: {tool_name}"
            
            response.raise_for_status()
            return json.dumps(response.json(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

async def pitaj_llm(poruka: str, temperature: float = 0.5) -> str:
    client, model = get_llm_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": poruka}
    ]

    odgovor = await client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=temperature,
        max_tokens=1024
    )

    msg = odgovor.choices[0].message    

    if not msg.tool_calls:
        return msg.content or ""

    # Obrada svih tool calls-a
    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments)
        rezultat_funkcije = await execute_tool(tc.function.name, args)
        
        # Ako messages zadnji nema model_dump, potrebno je prvo ubaciti assistant poruku
        if msg not in messages:
            messages.append(msg.model_dump(exclude_none=True))
            
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": rezultat_funkcije
        })

    odgovor_2 = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=1024
    )

    return odgovor_2.choices[0].message.content or ""

class ChatRequest(BaseModel):
    poruka: str = Field(..., description="Korisnicka poruka")
    temperature: float = Field(0.5, description="Temperatura za generisanje odgovora")

class ChatResponse(BaseModel):
    odgovor: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(zahtjev: ChatRequest) -> ChatResponse:
    try:
        odgovor = await pitaj_llm(zahtjev.poruka, zahtjev.temperature)
        return ChatResponse(odgovor=odgovor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
