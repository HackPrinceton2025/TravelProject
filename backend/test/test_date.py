"""
Test date handling in agent
"""
import asyncio
import json
from agent.runner import get_travel_agent


async def test_relative_date():
    """Test handling of relative dates like 'November'"""
    print("=" * 80)
    print("TEST: Relative Date Handling")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "I want to go on a trip to NYC in November. Any exiting events?"
    
    print(f"Query: {message}\n")
    print(f"Current Date: 2025-11-08 (November)")
    print(f"Expected: Agent should interpret 'November' as November 2025\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_date",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"])
    print()
    
    # Check if the response mentions 2025
    if "2025" in result["message"]:
        print("✅ Correctly interpreted as November 2025")
    else:
        print("ℹ️  No specific year mentioned")
    
    print("\n" + "=" * 80 + "\n")

async def test_past_month():
    """Test handling of past month"""
    print("=" * 80)
    print("TEST: Past Month")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "I want to travel to NYC in March. Any exiting events?"
    
    print(f"Query: {message}\n")
    print(f"Current Date: 2025-11-08")
    print(f"Expected: Agent should interpret 'March' as March 2026 (upcoming)\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_date_2",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"])
    print()
    
    if "2026" in result["message"] and "March" in result["message"]:
        print("✅ Correctly interpreted as March 2026")
    elif "2025" in result["message"]:
        print("⚠️  Incorrectly used March 2025")
    else:
        print("ℹ️  No specific year mentioned")
    
    print("\n" + "=" * 80 + "\n")

async def test_future_month():
    """Test handling of future month"""
    print("=" * 80)
    print("TEST: Future Month")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "I want to travel to NYC in December. Any exiting events?"
    
    print(f"Query: {message}\n")
    print(f"Current Date: 2025-11-08")
    print(f"Expected: Agent should interpret 'December' as December 2025 (upcoming)\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_date_2",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"])
    print()
    
    if "2025" in result["message"] and "December" in result["message"]:
        print("✅ Correctly interpreted as December 2025")
    elif "2026" in result["message"]:
        print("⚠️  Incorrectly used December 2026")
    else:
        print("ℹ️  No specific year mentioned")
    
    print("\n" + "=" * 80 + "\n")


async def main():
    """Run date handling tests"""
    print("\n📅 Starting Date Handling Tests\n")
    
    #await test_relative_date()
    await test_past_month()
    #await test_future_month()
    
    print("✅ All date tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
