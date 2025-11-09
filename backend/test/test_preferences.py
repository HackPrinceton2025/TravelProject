"""
Test preferences tools
"""
import asyncio
import json
from agent.runner import get_travel_agent


async def test_get_user_preferences():
    """Test getting user preferences"""
    print("=" * 80)
    print("TEST: Get User Preferences")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "What are my travel preferences?"
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        user_id="d921a507-969c-4aec-a821-b643747cbf41",
        group_id="4ae635cd-eb86-4734-b072-ca76caf5963c",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"][:200] + "..." if len(result["message"]) > 200 else result["message"])
    print()
    
    if result["cards"]:
        print(f"💳 Cards Returned: {len(result['cards'])}")
        for i, card in enumerate(result["cards"], 1):
            print(f"\n  Card {i}:")
            print(f"    Type: {card['type']}")
            if card['type'] == 'user_preferences':
                data = card['data']
                print(f"    Departure City: {data.get('departure_city')}")
                print(f"    Budget Max: ${data.get('budget_max')}")
                print(f"    Interests: {data.get('interests')}")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_get_all_group_preferences():
    """Test getting all group members' preferences"""
    print("=" * 80)
    print("TEST: Get All Group Preferences")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Show me everyone's travel preferences and find what we have in common."
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        user_id="06f5a1b5-5339-4368-8781-9baeaa4c9ba1",
        group_id="d1624f51-79d8-403f-ba0a-419f2bdd7b84",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"][:300] + "..." if len(result["message"]) > 300 else result["message"])
    print()
    
    if result["cards"]:
        print(f"💳 Cards Returned: {len(result['cards'])}")
        
        # Count card types
        user_pref_count = sum(1 for c in result["cards"] if c['type'] == 'user_preferences')
        consensus_count = sum(1 for c in result["cards"] if c['type'] == 'group_consensus')
        
        print(f"  - User Preferences: {user_pref_count}")
        print(f"  - Group Consensus: {consensus_count}")
        
        # Show individual preferences with custom items highlighted
        print(f"\n  👥 Individual Preferences:")
        for card in result["cards"]:
            if card['type'] == 'user_preferences':
                data = card['data']
                print(f"\n    {data.get('user_name')}:")
                print(f"      Interests: {data.get('interests')}")
                print(f"      Dietary: {data.get('dietary_restrictions')}")
                print(f"      Pace: {data.get('travel_pace')}")
        
        # Show consensus if available
        for card in result["cards"]:
            if card['type'] == 'group_consensus':
                print(f"\n  📊 Group Consensus (predefined items only):")
                data = card['data']
                print(f"    Total Members: {data.get('total_members')}")
                print(f"    Budget Range: ${data.get('budget_range', {}).get('min')} - ${data.get('budget_range', {}).get('max')}")
                print(f"    Common Interests: {data.get('common_interests')}")
                print(f"    Common Dietary: {data.get('dietary_restrictions')}")
                print(f"    Preferred Pace: {data.get('preferred_travel_pace')}")
                print(f"    Overlapping Dates: {data.get('overlapping_dates')}")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_update_preferences_with_custom():
    """Test updating preferences with custom items"""
    print("=" * 80)
    print("TEST: Update Preferences with Custom Items")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Update my preferences: I'm interested in food, I'm vegeterian, and my budget would be $1000."
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        user_id="d921a507-969c-4aec-a821-b643747cbf41",
        group_id="4ae635cd-eb86-4734-b072-ca76caf5963c",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"][:300] + "..." if len(result["message"]) > 300 else result["message"])
    print()
    
    if result["cards"]:
        print(f"💳 Cards Returned: {len(result['cards'])}")
        for card in result["cards"]:
            if card['type'] == 'confirmation':
                data = card['data']
                print(f"\n  ✅ Update Status: {data.get('success')}")
                print(f"  Message: {data.get('message')}")
                print(f"  Updated Fields: {data.get('updated_fields')}")
                
                # Show normalized preferences
                if 'updated_preferences' in data:
                    prefs = data['updated_preferences']
                    print(f"\n  📝 Normalized Preferences:")
                    if 'interests' in prefs:
                        print(f"    Interests: {prefs['interests']}")
                        print(f"      (Museums: predefined, Wine Tasting: custom)")
                    if 'dietary_restrictions' in prefs:
                        print(f"    Dietary: {prefs['dietary_restrictions']}")
                        print(f"      (Pescatarian: custom)")
                    if 'travel_pace' in prefs:
                        print(f"    Pace: {prefs['travel_pace']}")
                        print(f"      (Relaxed: predefined)")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_update_custom_fields():
    """Test updating preferences with custom fields"""
    print("=" * 80)
    print("TEST: Update Custom Preference Fields")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "Update my preferences: I prefer luxury accommodations and small group sizes (under 10 people)"
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_group_custom",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"][:300] + "..." if len(result["message"]) > 300 else result["message"])
    print()
    
    if result["cards"]:
        print(f"💳 Cards Returned: {len(result['cards'])}")
        for card in result["cards"]:
            if card['type'] == 'confirmation':
                data = card['data']
                print(f"\n  ✅ Update Status: {data.get('success')}")
                print(f"  Message: {data.get('message')}")
                print(f"  Updated Fields: {data.get('updated_fields')}")
                
                # Show custom fields
                if 'updated_preferences' in data:
                    prefs = data['updated_preferences']
                    print(f"\n  📝 Custom Fields:")
                    for key, value in prefs.items():
                        print(f"    {key}: {value}")
                    print(f"\n  💡 Expected custom_fields usage:")
                    print(f"    - accommodation_style: luxury")
                    print(f"    - group_size_preference: small (under 10)")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def test_preference_schema():
    """Test getting preference schema for a group"""
    print("=" * 80)
    print("TEST: Get Preference Schema")
    print("=" * 80)
    
    agent = get_travel_agent()
    message = "What preference fields are we tracking for this trip?"
    
    print(f"Query: {message}\n")
    
    result = await agent.chat(
        message=message,
        group_id="test_group_schema",
        stream=False
    )
    
    print("📝 Agent Message:")
    print(result["message"][:200] + "..." if len(result["message"]) > 200 else result["message"])
    print()
    
    if result["cards"]:
        for card in result["cards"]:
            if card['type'] == 'preference_schema':
                print("📋 Preference Schema:")
                data = card['data']
                print(f"\n  Required Fields ({len(data.get('required_fields', []))}):")
                for field in data.get('required_fields', []):
                    print(f"    - {field['label']} ({field['type']})")
                
                print(f"\n  Optional Fields ({len(data.get('optional_fields', []))}):")
                for field in data.get('optional_fields', []):
                    print(f"    - {field['label']} ({field['type']})")
    else:
        print("⚠️  No cards returned")
    
    print("\n" + "=" * 80 + "\n")


async def main():
    """Run preference tests"""
    print("\n⚙️  Starting Preferences Tool Tests\n")
    
    #await test_get_user_preferences()
    await test_get_all_group_preferences()
    #await test_update_preferences_with_custom()
    #await test_update_custom_fields()
    #await test_preference_schema()
    
    print("✅ All preference tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
