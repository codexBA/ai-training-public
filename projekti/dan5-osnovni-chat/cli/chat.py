# osnovni chat - command line interface = CLI
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import pitaj_llm

async def main_async():
    print("=== Osnovni Chat ===")
    print("Unesi 'izlaz' za prekid.\n")

    while True: # beskonačna petlja dok se ne unese 'izlaz'
        poruka = input("Tvoja poruka: ")
        # ako korisnik unese rijec 'izlaz', program se gasi
        if poruka.lower() == "izlaz":
            print("Doviđenja.")
            return
        
        odgovor = await pitaj_llm(poruka, temperature=0.7)
        print(f"AI odgovor: {odgovor}\n")
  
if __name__ == "__main__":
    asyncio.run(main_async())