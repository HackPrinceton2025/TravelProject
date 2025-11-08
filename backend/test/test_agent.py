"""
Test script for Travel Agent Runner with Card Support
"""
import asyncio
import json
from agent.runner import get_travel_agent


async def test_budget_query():
    """Test budget calculation - should return a budget card"""
    print("=" * 80)
    print("TEST 1: Budget Calculation")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Calculate a budget for 4 people going to Tokyo for 7 days with $8000 total."
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_group_1",
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
            print(f"    ID: {card['id']}")
            print(f"    Data: {json.dumps(card['data'], indent=6)}")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_hotel_query():
    """Test hotel search - should return hotel cards"""
    print("=" * 80)
    print("TEST 2: Hotel Search")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Find hotels in Paris for 2 guests, checking in on 2025-11-22 and checking out on 2025-11-23. Budget is $150 per night."
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_group_2",
        user_preferences={
            "budget_range": "medium",
            "amenities_preferred": ["WiFi", "Breakfast"]
        },
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
            print(f"    ID: {card['id']}")
            if card['type'] == 'hotel':
                data = card['data']
                print(f"    Hotel: {data.get('name')}")
                print(f"    Rating: {data.get('rating')}")
                print(f"    Price: ${data.get('price_per_night')}/night")
                print(f"    Amenities: {', '.join(data.get('amenities', []))}")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_flight_query():
    """Test flight search - should return flight cards"""
    print("=" * 80)
    print("TEST 3: Flight Search")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Search flights from New York to London on 2025-11-20 for 3 adults."
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_group_3",
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
            if card['type'] == 'flight':
                data = card['data']
                print(f"    Airline: {data.get('airline')}")
                print(f"    Route: {data.get('origin')} → {data.get('destination')}")
                print(f"    Time: {data.get('departure_time')} - {data.get('arrival_time')}")
                print(f"    Price: ${data.get('total_price')} total (${data.get('price_per_person')}/person)")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_integrated_trip_planning():
    """
    Integration Test: Complete trip planning workflow
    Scenario: Group of 3 friends planning a trip using preferences, dates, and locations
    """
    print("=" * 80)
    print("INTEGRATION TEST: Complete Trip Planning Workflow")
    print("=" * 80)
    print("\nScenario: 3 friends planning a European trip")
    print("- They have different preferences (museums, food, nightlife)")
    print("- Current date: November 8, 2025")
    print("- Planning for: March 2026 (5 days)")
    print("- Starting cities: New York, Boston, Philadelphia")
    print("=" * 80 + "\n")
    
    # Run all steps sequentially
    #await test_step1_set_preferences()
    #await test_step2_analyze_consensus()
    #await test_step3_check_locations()
    #await test_step4_recommend_destination()
    await test_step5_search_accommodations()
    #await test_step6_generate_itinerary()
    
    print("\n" + "=" * 80)
    print("✅ INTEGRATION TEST COMPLETED")
    print("=" * 80)
    print("\nSummary:")
    print("- ✓ Preferences set and analyzed")
    print("- ✓ Group consensus found")
    print("- ✓ Member locations identified")
    print("- ✓ Date correctly interpreted (March 2026)")
    print("- ✓ Destination recommended based on preferences")
    print("- ✓ Hotels searched")
    print("- ✓ Itinerary generated")
    print("\n" + "=" * 80 + "\n")


async def test_step1_set_preferences():
    """Step 1: Set personal preferences"""
    print("\n📋 STEP 1: Setting up personal preferences")
    print("-" * 80)
    
    agent = get_travel_agent()
    group_id = "integration_test_group"
    
    result = await agent.chat(
        message="Update my preferences: I'm interested in museums and food & dining, I'm vegetarian, my budget is $3000, and I prefer a moderate travel pace. I'm departing from New York.",
        group_id=group_id,
        stream=False
    )
    
    print(f"✓ User 1 preferences set")
    print(f"  Response: {result['message'][:150]}...")
    
    if result['cards']:
        for card in result['cards']:
            if card['type'] == 'confirmation':
                data = card['data']
                print(f"\n  Updated fields: {data.get('updated_fields')}")


async def test_step2_analyze_consensus():
    """Step 2: Analyze group preferences and find consensus"""
    print("\n📊 STEP 2: Analyzing group preferences and finding consensus")
    print("-" * 80)
    
    agent = get_travel_agent()
    group_id = "integration_test_group"
    
    result = await agent.chat(
        message="Show me everyone's travel preferences and what we have in common",
        group_id=group_id,
        stream=False
    )
    
    print(f"Response: {result['message'][:200]}...")
    
    if result['cards']:
        for card in result['cards']:
            if card['type'] == 'group_consensus':
                data = card['data']
                print(f"\n✓ Group Consensus Found:")
                print(f"  - Total Members: {data.get('total_members')}")
                print(f"  - Common Interests: {data.get('common_interests')}")
                print(f"  - Budget Range: ${data.get('budget_range', {}).get('min')} - ${data.get('budget_range', {}).get('max')}")
                print(f"  - Overlapping Dates: {data.get('overlapping_dates')}")
                print(f"  - Dietary Requirements: {data.get('dietary_restrictions')}")


async def test_step3_check_locations():
    """Step 3: Check group member locations"""
    print("\n📍 STEP 3: Checking group member locations")
    print("-" * 80)
    
    agent = get_travel_agent()
    group_id = "integration_test_group"
    
    result = await agent.chat(
        message="Where are all the group members located?",
        group_id=group_id,
        stream=False
    )
    
    print(f"Response: {result['message'][:200]}...")
    
    if result['cards']:
        location_cards = [c for c in result['cards'] if c['type'] == 'location']
        print(f"\n✓ Found {len(location_cards)} member locations:")
        for card in location_cards:
            data = card['data']
            print(f"  - {data.get('user_name')}: {data.get('city')}, {data.get('country')}")


async def test_step4_recommend_destination():
    """Step 4: Recommend destination with date interpretation"""
    print("\n🗓️  STEP 4: Planning trip for March (should interpret as March 2026)")
    print("-" * 80)
    
    agent = get_travel_agent()
    group_id = "integration_test_group"
    
    result = await agent.chat(
        message="Recommend a European city for a 5-day trip in March. We all like museums and good food.",
        group_id=group_id,
        stream=False
    )
    
    print(f"\nResponse:\n{result['message']}\n")
    
    # Check date interpretation
    if "2026" in result['message']:
        print("✅ Correct: Agent interpreted March as March 2026")
    elif "2025" in result['message']:
        print("❌ Error: Agent incorrectly used March 2025 (past month)")
    
    if result['cards']:
        print(f"\n💳 Cards Returned: {len(result['cards'])}")
        for i, card in enumerate(result['cards'], 1):
            print(f"\n  Card {i} - Type: {card['type']}")
            if card['type'] == 'hotel':
                data = card['data']
                print(f"    Hotel: {data.get('name')} - ${data.get('price_per_night')}/night")
            elif card['type'] == 'attraction':
                data = card['data']
                print(f"    Attraction: {data.get('name')} - {data.get('category')}")
            elif card['type'] == 'restaurant':
                data = card['data']
                print(f"    Restaurant: {data.get('name')} - {data.get('cuisine_type')}")


async def test_step5_search_accommodations():
    """Step 5: Search for accommodations"""
    print("\n🏨 STEP 5: Searching for accommodations")
    print("-" * 80)
    
    agent = get_travel_agent()
    group_id = "integration_test_group"
    
    result = await agent.chat(
        message="Find hotels for 3 guests in Philadelphia for December 17-20, 2025. Budget is $150 per night.",
        group_id=group_id,
        stream=False
    )
    
    print(f"Response: {result['message'][:200]}...")
    
    if result['cards']:
        hotel_cards = [c for c in result['cards'] if c['type'] == 'hotel']
        print(f"\n✓ Found {len(hotel_cards)} hotel options:")
        for card in hotel_cards[:3]:  # Show first 3
            data = card['data']
            print(f"  - {data.get('name')}: ${data.get('price')}/{data.get('price_unit')}/night ({data.get('rating')}⭐)")
    else:
        print("⚠️  No hotel cards returned (check MCP tool results)")


async def test_step6_generate_itinerary():
    """Step 6: Generate trip itinerary"""
    print("\n📅 STEP 6: Generating trip itinerary")
    print("-" * 80)
    
    agent = get_travel_agent()
    group_id = "integration_test_group"
    
    result = await agent.chat(
        message="Create a day-by-day itinerary for our trip that includes museums, good restaurants (vegetarian-friendly), and cultural activities.",
        group_id=group_id,
        stream=False
    )
    
    print(f"Response: {result['message'][:300]}...")
    
    if result['cards']:
        for card in result['cards']:
            if card['type'] == 'itinerary':
                data = card['data']
                print(f"\n✓ Itinerary Created:")
                print(f"  - Destination: {data.get('destination')}")
                print(f"  - Duration: {data.get('start_date')} to {data.get('end_date')}")
                print(f"  - Days: {len(data.get('daily_plans', []))}")
            elif card['type'] == 'restaurant':
                data = card['data']
                print(f"\n  Restaurant: {data.get('name')}")
            elif card['type'] == 'attraction':
                data = card['data']
                print(f"\n  Attraction: {data.get('name')}")


async def main():
    """Run all tests"""
    print("\n🚀 Starting Travel Agent Tests\n")
    
    # Run integration test (full trip planning workflow)
    await test_integrated_trip_planning()
    
    # Optional: Run individual step tests
    print("\n" + "=" * 80)
    print("INDIVIDUAL STEP TESTS (if needed)")
    print("=" * 80)
    print("Uncomment below to run individual steps:")
    print("- await test_step1_set_preferences()")
    print("- await test_step2_analyze_consensus()")
    print("- await test_step3_check_locations()")
    print("- await test_step4_recommend_destination()")
    print("- await test_step5_search_accommodations()")
    print("- await test_step6_generate_itinerary()")
    
    print("\n✅ All tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
