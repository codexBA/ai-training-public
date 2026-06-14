# Napomena: python:3.11-slim koristimo u Dockeru za konzistentnost između mašina.
# Na Windows laptopu možete imati 3.11, 3.12 ili 3.13 — sve verzije su kompatibilne.
FROM python:3.11-slim

WORKDIR /app

# Instaliramo Python zavisnosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiramo aplikacijski kod
COPY . .

# Otvaramo port 8001 za FastAPI
EXPOSE 8001

# Pokrećemo uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
