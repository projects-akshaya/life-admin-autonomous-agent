# app.py
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()


from google.adk.runners import InMemoryRunner
from agents.life_admin.agent import app


async def main():
    runner = InMemoryRunner(app=app)

    print("Life-Admin Agent")
    print("----------------")
    print("Paste your messy life-admin tasks (empty line to finish):\n")

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line)

    user_text = "\n".join(lines)
    if not user_text.strip():
        print("No input provided, exiting.")
        return

    result = await runner.run_debug(user_text)


if __name__ == "__main__":
    # Make sure GOOGLE_API_KEY is set
    if "GOOGLE_API_KEY" not in os.environ:
        print("WARNING: GOOGLE_API_KEY is not set. Set it or use a .env loader.")
    asyncio.run(main())
