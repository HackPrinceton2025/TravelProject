"""
Test location tools
"""
import asyncio
import json
from agent.runner import get_travel_agent


async def test_user_location():
    """Test getting user location"""
    print("=" * 80)
    print("TEST: User Location")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Where am I located? Show me my current location."
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_location",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"])
    print()
    
    if result["cards"]:
        print(f"💳 Cards Returned: {len(result['cards'])}")
        for i, card in enumerate(result["cards"], 1):
            print(f"\n  Card {i}:")
            print(f"    Type: {card['type']}")
            print(f"    Data: {json.dumps(card['data'], indent=6)}")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_group_locations():
    """Test getting group members' locations"""
    print("=" * 80)
    print("TEST: Group Members Locations")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Show me where all group members are located. We need to find a good meetup spot."
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_group_123",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"])
    print()
    
    if result["cards"]:
        print(f"💳 Cards Returned: {len(result['cards'])}")
        for i, card in enumerate(result["cards"], 1):
            print(f"\n  Card {i}:")
            print(f"    Type: {card['type']}")
            if card['type'] == 'location':
                data = card['data']
                print(f"    User: {data.get('user_name', 'Unknown')}")
                print(f"    City: {data.get('city')}")
                print(f"    Country: {data.get('country')}")
                print(f"    Coordinates: {data.get('coordinates')}")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def main():
    """Run location tests"""
    print("\n🗺️  Starting Location Tool Tests\n")
    
    await test_user_location()
    await test_group_locations()
    
    print("✅ All location tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
