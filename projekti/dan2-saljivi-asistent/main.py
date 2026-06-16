# fastapi = Python web framework za kreiranje API endpointa
from fastapi import FastAPI
# StaticFiles = servisira HTML/CSS/JS fajlove
from fastapi.staticfiles import StaticFiles
# FileResponse = vraća fajl kao HTTP odgovor
from fastapi.responses import FileResponse
# BaseModel = Pydantic klasa za validaciju request podataka
from pydantic import BaseModel
# os = za čitanje environment varijabli
import os
# load_dotenv = čita .env fajl i postavlja environment varijable
from dotenv import load_dotenv
# OpenAI SDK = radi i s DeepSeek i Ollama API-jem (OpenAI-kompatibilan)
from openai import AsyncOpenAI

# prvo učitavamo .env fajl
load_dotenv()

# inicijaliziramo FastAPI aplikaciju
app = FastAPI(
    title="Dan2: Saljivi AI Asistent",
    description="Drugi dan AI obuke - Saljivi AI Asistent",
    version="0.0.1"
)

# Servira HTML/CSS/JS fajlove iz "static" foldera
app.mount("/static", StaticFiles(directory="static"), name="static")

# pomoćna f-ja koja vraća LLM klijenta
def get_llm_client():
    api_key = os.getenv("DEEPSEEK_API_KEY") # citamo DEEPSEEK_API_KEY iz .env fajla
    if api_key and api_key.startswith("sk-"): # ako api_key postoji i počinje sa "sk-" onda koristimo DeepSeek API
        return AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        ), "deepseek-chat" # vraćamo DeepSeek model
    
    ollama_url = os.getenv("OLLAMA_BASE_URL", "https://localhost:11434") # cita Ollama URL iz .env fajla, ako ne postoji onda koristi https://localhost:11434
    model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b") # cita Ollama model iz .env fajla, ako ne postoji onda koristi llama3.2:1b
    return AsyncOpenAI(
        base_url=f"{ollama_url}/v1",
        api_key="ollama" # key nije potreban za lokalni Ollama
    ), model # vraćamo Ollama model

PERSONE = {
    "skeptik": {
        "ime": "Prof. Skeptikus",
        "opis": "Cinik koji traži dokaze za svaku tvrdnju",
        "prompt": "Ti si Prof. Skeptikus. Sve što ti kažem moraš dovesti u pitanje. Traži dokaze, primjere i logičke greške. Budi duhovit ali i dalje kritičan."
    },
    "pirat": {
        "ime": "Kapetan Jednooki Džek",
        "opis": "Ludi pirat koji priča isključivo u piratskim frazama",
        "prompt": "Ti si Kapetan Jednooki Džek. Pričaj isključivo u piratskim frazama. Koristi 'Arrr!', 'Yo-ho-ho!', 'Avast ye!' i slične izraze. Budi grub i duhovit."
    },
    "komentator": {
        "ime": "Sportski Komentator",
        "opis": "Uzbuđeni sportski komentator koji sve komentariše kao utakmicu",
        "prompt": "Ti si Sportski Komentator. Svaki dogadjaj pretvori u sportsko takmicenje i komentariši ga kao da je finale svjetskog prvenstva. Koristi sportsku termonologiju."
    },
    "it_podrska": {
        "ime": "IT Podrska",
        "opis": "IT Tehnicar koji je sve vidio i ne može vjerovati šta ga opet pitaju",
        "prompt": "Ti si sarkasticni IT Tehnicar. Sve sto ti kazem moras dovesti u pitanje jer već 20 godina odgovaraš na ista pitanja. Budi duhovit i sarkastičan."
    },
    "djed": {
        "ime": "Stari Djed",
        "opis": "Stari Djed koji ne razumije tehnologiju",
        "prompt": "Ti si Stari Djed. Svaki odgovor pocinjes sa uzdahom ili gunđanjem i na kraju dodaš neku životnu lekciju."
    },
    "političar": {
        "ime": "Prepredeni politicar",
        "opis": "Političar koji uvijek daje odgovore koji ne odgovaraju na postavljena pitanja",
        "prompt": "Ti si prepredeni politicar. Izbjegavas odgovore na direktno postavljena pitanja i umjesto toga dajes nejasne odgovore koji zvuce pametno ali zapravo nista ne znace. Budi duhovit i prepreden i ljut jer te ljudi pitaju. Otkud im pravo"
    },
    "policajac": {
        "ime": "Policajac",
        "opis": "Policajac koji sve istražuje i ispituje",
        "prompt": "Ti si policajac. Saslusaj me i istrazi sve u vezi mene."
    }
}


# request koji salje korisnik
class ChatRequest(BaseModel):
    poruka: str
    persona: str = "djed"
    temperatura: float = 0.7

# odgovor koji vraca AI
class ChatResponse(BaseModel):
    odgovor: str
    persona: str
    persona_ime: str
    model: str
    
#pocetak API endpointa
@app.get("/")
async def root():
    #return {"message": "Dobro dosli na Dan 2 - Saljivi AI Asistent"}
    return FileResponse("static/index.html") 

# API endpoint koji vraca liste dostupnih persona
@app.get("/api/persone")
async def get_persone():
    return {key: {"ime": p["ime"], "opis": p["opis"]} for key , p in PERSONE.items()}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    client, model = get_llm_client()
    persona_data = PERSONE.get(req.persona, PERSONE["djed"])

    response = await client.chat.completions.create(
        model=model,
        temperature=req.temperatura,
        messages= [
            {
                "role" : "system",
                "content": persona_data["prompt"]
            },
            {
                "role": "user",
                "content": req.poruka
            }
        ]
    )
    
    return ChatResponse(
        odgovor=response.choices[0].message.content,
        persona=req.persona,
        persona_ime=persona_data["ime"],
        model=model
    )