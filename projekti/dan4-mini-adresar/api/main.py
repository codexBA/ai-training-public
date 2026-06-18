from data_store import list_osobe
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

_PROJECT_ROOT = Path(__file__).parent.parent

load_dotenv(dotenv_path=_PROJECT_ROOT / ".env")

app = FastAPI(
    title="Dan4 - Mini Adresar - JSON Reader",
    description="Cetvrti dan AI obuke - Mini Adresar - JSON Reader",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"poruka": "Dobro dosao u Mini Adresar - JSON Reader"}

# izlistaj sve osobe
@app.get("/osobe")
async def osobe():
    return list_osobe()