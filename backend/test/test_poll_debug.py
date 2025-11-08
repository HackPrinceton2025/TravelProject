"""
Debug poll status retrieval
"""
import asyncio
from agent.runner import get_travel_agent


async def test_poll_status_query():
    """Test if agent can retrieve poll status"""
    print("=" * 80)
    print("DEBUG: Poll Status Query")
    print("=" * 80)
    
    agent = get_travel_agent()
    
    # Step 1: Create a poll
    print("\n1️⃣ Creating a poll...")
    result1 = await agent.chat(
        message="Create a poll asking 'Where should we go for dinner?' with options: Italian Restaurant, Korean BBQ, Sushi Place",
        user_id="d921a507-969c-4aec-a821-b643747cbf41",
        group_id="4ae635cd-eb86-4734-b072-ca76caf5963c",
        stream=False
    )
    
    print(f"Agent response: {result1['message'][:200]}...")
    
    poll_id = None
    if result1['cards']:
        for card in result1['cards']:
            if card['type'] == 'poll':
                poll_id = card['data'].get('poll_id')
                print(f"✅ Poll created: {poll_id}")
                break
    
    if not poll_id:
        print("❌ No poll ID found in response")
        print(f"Cards: {result1['cards']}")
        return
    
    # Step 2: Try to get poll status with explicit poll_id
    print(f"\n2️⃣ Querying poll status for {poll_id}...")
    result2 = await agent.chat(
        message=f"Show me the current status of poll {poll_id}",
        user_id="d921a507-969c-4aec-a821-b643747cbf41",
        group_id="4ae635cd-eb86-4734-b072-ca76caf5963c",
        stream=False
    )
    
    print(f"Agent response: {result2['message'][:300]}...")
    print(f"\nCards returned: {len(result2['cards'])}")
    
    if result2['cards']:
        for card in result2['cards']:
            print(f"  - Card type: {card['type']}")
            if card['type'] == 'poll':
                data = card['data']
                print(f"    Poll ID: {data.get('poll_id')}")
                print(f"    Status: {data.get('status')}")
                print(f"    Total votes: {data.get('total_votes')}")
                print(f"    Has majority: {data.get('has_majority')}")
    else:
        print("⚠️ No cards returned - agent didn't call get_poll_status")
    
    # Step 3: Try generic query
    print(f"\n3️⃣ Generic poll status query...")
    result3 = await agent.chat(
        message="Show me the voting results for the dinner poll",
        user_id="d921a507-969c-4aec-a821-b643747cbf41",
        group_id="4ae635cd-eb86-4734-b072-ca76caf5963c",
        stream=False
    )
    
    print(f"Agent response: {result3['message'][:300]}...")
    print(f"Cards returned: {len(result3['cards'])}")
    
    if result3['cards']:
        for card in result3['cards']:
            print(f"  - Card type: {card['type']}")
    else:
        print("⚠️ No cards returned")
    
    # Step 4: Check tool calls in result
    print(f"\n4️⃣ Checking tool usage...")
    print(f"Result 2 metadata: {result2.get('metadata', {})}")
    
    print("\n" + "=" * 80)


async def test_direct_tool_call():
    """Test calling get_poll_status directly"""
    print("=" * 80)
    print("DEBUG: Direct Tool Call")
    print("=" * 80)
    
    from agent.tools.polls import create_poll, get_poll_status, get_latest_poll
    
    # Use real group_id that exists in database
    real_group_id = "4ae635cd-eb86-4734-b072-ca76caf5963c"
    real_user_id = "d921a507-969c-4aec-a821-b643747cbf41"
    
    # Create poll directly
    print("\n1️⃣ Creating poll directly...")
    try:
        poll_result = create_poll(
            group_id=real_group_id,
            question="Test question?",
            options=[
                {"text": "Option A"},
                {"text": "Option B"},
                {"text": "Option C"}
            ],
            created_by=real_user_id,
            poll_type="custom"
        )
        
        print(f"Poll result type: {poll_result.get('type')}")
        print(f"Has cards: {len(poll_result.get('cards', []))}")
        
        # Extract poll_id from cards, not metadata
        poll_id = None
        if poll_result.get('cards'):
            first_card = poll_result['cards'][0]
            print(f"First card type: {first_card.get('type')}")
            print(f"Card data keys: {list(first_card.get('data', {}).keys())}")
            poll_id = first_card.get('data', {}).get('poll_id')
        
        print(f"✅ Poll created: {poll_id}")
        
        if not poll_id:
            print("❌ Failed to get poll_id")
            print(f"Full result: {poll_result}")
            return
            
    except Exception as e:
        print(f"❌ Error creating poll: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Get status directly
    print(f"\n2️⃣ Getting poll status directly...")
    try:
        status_result = get_poll_status(
            poll_id=poll_id,
            group_id=real_group_id,
        )
        
        print(f"Result type: {status_result['type']}")
        print(f"Cards: {len(status_result['cards'])}")
        
        if status_result['cards']:
            card = status_result['cards'][0]
            data = card['data']
            print(f"  Poll ID: {data.get('poll_id')}")
            print(f"  Question: {data.get('question')}")
            print(f"  Status: {data.get('status')}")
            print(f"  Total votes: {data.get('total_votes')}")
            print(f"  Total members: {data.get('total_members')}")
            print(f"  Has majority: {data.get('has_majority')}")
    except Exception as e:
        print(f"❌ Error getting poll status: {e}")
        import traceback
        traceback.print_exc()
    
    # Test get_latest_poll
    print(f"\n3️⃣ Testing get_latest_poll...")
    try:
        latest_result = get_latest_poll(group_id=real_group_id)
        
        print(f"Result type: {latest_result['type']}")
        if latest_result['type'] == 'poll_status':
            card = latest_result['cards'][0]
            data = card['data']
            print(f"  ✅ Found latest poll: {data.get('poll_id')}")
            print(f"  Question: {data.get('question')}")
        else:
            print(f"  ⚠️ No active poll found or error occurred")
    except Exception as e:
        print(f"❌ Error getting latest poll: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)


async def main():
    print("\n🔍 Starting Poll Status Debug Tests\n")
    
    await test_direct_tool_call()
    print("\n")
    await test_poll_status_query()
    
    print("\n✅ Debug tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
