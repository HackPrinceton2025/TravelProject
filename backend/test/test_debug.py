"""Quick debug test for card extraction"""
import asyncio
from agent.runner import get_travel_agent


async def main():
    agent = get_travel_agent()
    
    result = await agent.chat(
        message="Find hotels in Paris for 2 guests, checking in on 2025-06-01.",
        group_id="debug_test",
        stream=False
    )
    
    print("\n" + "="*80)
    print("FINAL RESULT:")
    print("="*80)
    print(f"Message length: {len(result['message'])}")
    print(f"Cards count: {len(result['cards'])}")
    print(f"Cards: {result['cards']}")


if __name__ == "__main__":
    asyncio.run(main())
