import requests

BASE_URL = "http://localhost:8052"

def main():
    print("=== Dobro dosli na Kviz Majstor! ===")    
    print("=== Unesi 'izlaz' za prekid razgovora ===\n")

    while True:
        poruka = input("\nPritisni Enter za novo pitanje ili 'izlaz' za prekid: ")
        if poruka.lower().strip() == 'izlaz':
            break
        
        # daj random pitanje iz JSON-a
        pitanje_data = requests.get(f"{BASE_URL}/api/pitanje")
        pitanje_data.raise_for_status()
        pitanje = pitanje_data.json()

        # ispis pitanja - predstavi pitanje studentu: ispisi detalje o kategoriji, tezini i samo pitanje
        print(f"\nKategorija: {pitanje['kategorija']} | Tezina: {pitanje['tezina']}")
        print(f"\nPitanje: {pitanje['pitanje']}\n")

        # trazimo unos odgovora od studenta
        odgovor_studenta = input("Tvoj odgovor: ").strip()

        payload = {
            "pitanje_id": pitanje['id'],
            "odgovor_studenta": odgovor_studenta
        }
        
        rezultat = requests.post(f"{BASE_URL}/api/provjeri", json=payload)
        rezultat.raise_for_status()
        data = rezultat.json()

        print(f"\n--- REZULTAT ---")
        print(f"\nDa li je odgovor tacan: {data['tacno']}\n")
        print(f"Komentar sudije: {data['komentar']}\n")

        # ispis povratne informacije
        print(f"Bodovi: {data['bodovi']}\n")
        print(f"Tacan odgovor: {data['tacan_odgovor']}\n")

if __name__ == "__main__":
    main()
