# osnovni chat - najjednostavnij LLM klijent

import os # import operativnog sistema (za rad sa fajlovima)

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from openai import AsyncOpenAI

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
    "Ti si ljubazni asistent koji odgovara na bosanskom, hrvatskom ili srpskom jeziku."
    "Odgovaraj kratko i koncizno, maksimalno 4 recenice"
)

# asinhrona funkcija koja komunicira sa LLM
async def pitaj_llm(poruka: str, temperature: float = 0.7) -> str:
    client, model = get_llm_client()

    # ovim se salje zahtjev/pitanje modelu
    odgovor = await client.chat.completions.create(
        model=model, # model koji koristimo
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": poruka}
        ],
        temperature=temperature,
        max_tokens=512        
    )

    # vraca odgovor modela, ako odgovor ne postoji, vrati prazan string
    return odgovor.choices[0].message.content or ""