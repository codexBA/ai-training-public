import requests

BASE_URL = "http://localhost:8051"

def main():
    print("=== Dobro dosli na Chat Aplikaciju! ===")    

    # dobaviti listu persona
    response = requests.get(f"{BASE_URL}/api/persone")
    response.raise_for_status() # ako postoji problem sa serverom
    persone = response.json() # json response pretvaramo u python dict
    
    print("Dostupne persone:")
    for key, persona in persone.items():
        print(f"  - {key}: {persona['ime']}")

    odabrana_persona = input("\nUnesi ID persone (npr. djed): ").strip()

    print(f"\n--- Zapoceo si razgovor sa: {odabrana_persona}")
    print("--- Unesi 'izlaz' za prekid razgovora.\n")

    while True:
        poruka = input("\nTi: ")
        if poruka.lower().strip() == 'izlaz':
            break
        
        payload = {
            "poruka": poruka,
            "persona": odabrana_persona,
            "temperatura": 0.7
        }
        
        res = requests.post(f"{BASE_URL}/api/chat", json=payload)
        res.raise_for_status()
        data = res.json()

        print(f"\n{data['persona_ime']}: {data['odgovor']}\n")

if __name__ == "__main__":
    main()
