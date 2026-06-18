"""
Weather Agent — CLI chat s vidljivim function calling trace-om.
Demonstrira: AI bira alat, aplikacija izvršava, AI odgovara korisniku.

Pokretanje:
    python cli/weather_agent.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from main import DEFAULT_SYSTEM, TOOLS
from tools.weather import execute_tool


def get_client():
    key = os.getenv("DEEPSEEK_API_KEY", "")
    if key and key.startswith("sk-"):
        print("  Model: DeepSeek (cloud)")
        return OpenAI(api_key=key, base_url="https://api.deepseek.com"), "deepseek-chat"

    url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        httpx.get(f"{url}/api/tags", timeout=2.0)
        model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
        print(f"  Model: Ollama ({model})")
        return OpenAI(api_key="ollama", base_url=f"{url}/v1"), model
    except Exception:
        print("  GRESKA: Nema DeepSeek key ni Ollama!")
        raise SystemExit(1)


def main():
    print("=" * 60)
    print("  Dan 4 — Weather Agent (Function Calling CLI)")
    print("  Primjer: Kakva je prognoza za Sarajevo?")
    print("  /quit za izlaz")
    print("=" * 60)

    klijent, model = get_client()
    max_iter = 3

    while True:
        try:
            pitanje = input("\nVi: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDovidjenja!")
            break

        if not pitanje:
            continue
        if pitanje.lower() == "/quit":
            print("Dovidjenja!")
            break

        # Stateless: svako pitanje = nova lista (system + user), bez prethodnih poruka
        messages = [
            {"role": "system", "content": DEFAULT_SYSTEM},
            {"role": "user", "content": pitanje},
        ]

        pocetak = time.monotonic()
        for _ in range(max_iter):
            response = klijent.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.3,
                max_tokens=500,
            )
            msg = response.choices[0].message

            if not msg.tool_calls:
                print(f"\nAI: {msg.content}")
                print(f"  [{int((time.monotonic() - pocetak) * 1000)} ms]")
                break

            messages.append(msg.model_dump(exclude_none=True))

            for tc in msg.tool_calls:
                fn = tc.function.name
                args = tc.function.arguments or "{}"
                print(f"\n  [TOOL CALL] {fn}")
                print(f"  [ARGS] {args}")

                result = execute_tool(fn, args)
                preview = result[:200] + ("..." if len(result) > 200 else "")
                print(f"  [RESULT] {preview}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
        else:
            print("\nAI: Previse koraka alata — prekinuto.")


if __name__ == "__main__":
    main()
