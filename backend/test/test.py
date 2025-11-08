import os
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)

    result = await runner.run(
        input="Find the year GPT-5 released, and handoff to Claude to write a haiku about Elon Musk. Output this haiku. Use your tools.",
        model=["google/gemini-2.5"],
        mcp_servers=["windsor/brave-search-mcp"],
        stream=False
    )

    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())