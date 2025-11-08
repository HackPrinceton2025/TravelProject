"""
Test poll tools
"""
import asyncio
import json
from agent.runner import get_travel_agent


async def test_create_poll():
    """Test creating a poll for group decision"""
    print("=" * 80)
    print("TEST: Create Poll")
    print("=" * 80)
    
    agent = get_travel_agent()
    #message = "Create a poll asking 'Which hotel should we book?' with options: Hotel Le Marais for $120 per night, Hotel Montmartre for $95 per night, and Hotel Latin Quarter for $150 per night"
    message = "Create a poll for dinner menu with options: Korean, Japanese, Indian, American"

    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        user_id="33e3091e-98fa-468f-bf93-562c593232ff",
        group_id="1748878f-bbed-411a-bb6c-a0409b72efb9",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"][:300] + "..." if len(result["message"]) > 300 else result["message"])
    print()
    
    if result["cards"]:
        print(f"💳 Cards Returned: {len(result['cards'])}")
        for card in result["cards"]:
            if card['type'] == 'poll':
                data = card['data']
                print(f"\n  ✅ Poll Created:")
                print(f"    Poll ID: {data.get('poll_id')}")
                print(f"    Question: {data.get('question')}")
                print(f"    Options: {len(data.get('options', []))} options")
                print(f"    Type: {data.get('poll_type')}")
                print(f"    Status: {data.get('status')}")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_get_poll_results():
    """Test getting poll results"""
    print("=" * 80)
    print("TEST: Get Poll Results")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Show me the results of the hotel poll"
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        user_id="33e3091e-98fa-468f-bf93-562c593232ff",
        group_id="1748878f-bbed-411a-bb6c-a0409b72efb9",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"][:300] + "..." if len(result["message"]) > 300 else result["message"])
    print()
    
    if result["cards"]:
        print(f"💳 Cards Returned: {len(result['cards'])}")
        for card in result["cards"]:
            if card['type'] == 'poll':
                data = card['data']
                print(f"\n  📊 Poll Results:")
                print(f"    Poll ID: {data.get('poll_id')}")
                print(f"    Question: {data.get('question')}")
                print(f"    Status: {data.get('status')}")
                print(f"    Total Votes: {data.get('total_votes')} / {data.get('total_members')} members")
                print(f"    Participation: {data.get('participation_rate', 0):.1f}%")
                print(f"    Has Majority: {data.get('has_majority', False)}")
                print(f"\n    Options:")
                for option in data.get('options', []):
                    votes = option.get('votes', 0)
                    percentage = option.get('percentage', 0)
                    print(f"      • {option.get('text')}")
                    print(f"        Votes: {votes} ({percentage:.1f}%)")
                
                leader = data.get('leader')
                if leader:
                    print(f"\n    🏆 Current Leader:")
                    print(f"      {leader.get('text')}")
                    print(f"      {leader.get('votes')} votes ({leader.get('percentage', 0):.1f}%)")
                
                voted_users = data.get('voted_users', [])
                if voted_users:
                    print(f"\n    ✅ Voted Users: {len(voted_users)} users")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_list_active_polls():
    """Test listing all active polls"""
    print("=" * 80)
    print("TEST: List Active Polls")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Show me all active polls for our group"
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        user_id="33e3091e-98fa-468f-bf93-562c593232ff",
        group_id="1748878f-bbed-411a-bb6c-a0409b72efb9",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"][:300] + "..." if len(result["message"]) > 300 else result["message"])
    print()
    
    if result["cards"]:
        print(f"💳 Cards Returned: {len(result['cards'])}")
        poll_cards = [c for c in result["cards"] if c['type'] == 'poll']
        print(f"\n  📋 Active Polls: {len(poll_cards)}")
        for i, card in enumerate(poll_cards, 1):
            data = card['data']
            print(f"\n  Poll {i}:")
            print(f"    Poll ID: {data.get('poll_id')}")
            print(f"    Question: {data.get('question')}")
            print(f"    Status: {data.get('status')}")
            print(f"    Votes: {data.get('total_votes')} / {data.get('total_members')} members")
            print(f"    Options: {len(data.get('options', []))} options")
            print(f"    Created: {data.get('created_at')}")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_integrated_voting_scenario():
    """
    Integration Test: Complete voting workflow
    Scenario: Group deciding on a hotel through voting
    """
    print("=" * 80)
    print("INTEGRATION TEST: Group Voting Workflow")
    print("=" * 80)
    print("\nScenario: Group voting on hotel selection")
    print("=" * 80)
    
    agent = get_travel_agent()
    group_id = "integration_test_voting"
    
    # Step 1: Search for hotels based on preferences
    print("\n🏨 STEP 1: Finding hotel options based on group preferences")
    print("-" * 80)
    
    result1 = await agent.chat(
        message="Based on our group's preferences (budget $3000, interested in museums and food, vegetarian-friendly), find 3 hotel options in Paris for March 15-20, 2026",
        group_id=group_id,
        user_id="integration_user_1",
        stream=False
    )
    
    print(f"Response: {result1['message'][:200]}...")
    
    if result1['cards']:
        hotel_cards = [c for c in result1['cards'] if c['type'] == 'hotel']
        print(f"\n✓ Found {len(hotel_cards)} hotel options")
        hotel_options = []
        for card in hotel_cards[:3]:
            data = card['data']
            hotel_name = data.get('name')
            price = data.get('price_per_night')
            hotel_options.append(f"{hotel_name} (${price}/night)")
            print(f"  - {hotel_name}: ${price}/night")
    
    # Step 2: Create a poll for the group
    print("\n🗳️  STEP 2: Creating a poll for hotel selection")
    print("-" * 80)
    
    result2 = await agent.chat(
        message="Create a poll asking 'Which hotel should we book for our Paris trip?' with the hotel options we just found",
        group_id=group_id,
        user_id="integration_user_1",
        stream=False
    )
    
    print(f"Response: {result2['message'][:200]}...")
    
    poll_id = None
    if result2['cards']:
        for card in result2['cards']:
            if card['type'] == 'poll' and 'poll_id' in card.get('data', {}):
                data = card['data']
                poll_id = data.get('poll_id')
                print(f"\n✓ Poll Created:")
                print(f"  Poll ID: {poll_id}")
                print(f"  Question: {data.get('question')}")
                print(f"  Status: {data.get('status')}")
                print(f"  Options: {len(data.get('options', []))}")
    
    # Step 3: Check poll results
    print("\n📊 STEP 3: Checking current poll results")
    print("-" * 80)
    
    result3 = await agent.chat(
        message="Show me the voting results for the hotel poll",
        group_id=group_id,
        user_id="integration_user_1",
        stream=False
    )
    
    print(f"Response: {result3['message'][:200]}...")
    
    if result3['cards']:
        for card in result3['cards']:
            if card['type'] == 'poll':
                data = card['data']
                print(f"\n✓ Poll Status:")
                print(f"  Total Votes: {data.get('total_votes')} / {data.get('total_members')} members")
                print(f"  Participation: {data.get('participation_rate', 0):.1f}%")
                print(f"  Has Majority: {data.get('has_majority', False)}")
                
                leader = data.get('leader')
                if leader:
                    print(f"  Current Leader: {leader.get('text')} ({leader.get('votes')} votes)")
    
    # Step 4: Make decision based on voting
    print("\n✅ STEP 4: Making final decision based on voting results")
    print("-" * 80)
    
    result4 = await agent.chat(
        message="Based on the poll results, what hotel should we book and what's the next step?",
        group_id=group_id,
        user_id="integration_user_1",
        stream=False
    )
    
    print(f"\nResponse:\n{result4['message']}\n")
    
    print("\n" + "=" * 80)
    print("✅ VOTING INTEGRATION TEST COMPLETED")
    print("=" * 80)
    print("\nSummary:")
    print("- ✓ Hotel options found based on preferences")
    print("- ✓ Poll created for group voting")
    print("- ✓ Poll results retrieved")
    print("- ✓ Decision recommendation based on voting")
    print("\n" + "=" * 80 + "\n")


async def main():
    """Run poll tests"""
    print("\n⚙️  Starting Poll Tool Tests\n")
    
    await test_create_poll()
    await test_get_poll_results()
    await test_list_active_polls()
    #await test_integrated_voting_scenario()
    
    print("✅ All poll tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
