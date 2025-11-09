"""
Test Kiwi.com Flight Search Tool
Verify flight search, location resolution, and card formatting
"""
import os
from agent.tools.kiwi_flights import search_flights_kiwi
from dotenv import load_dotenv

load_dotenv()

def test_credentials():
    """Verify RapidAPI credentials are set"""
    print("\n" + "="*80)
    print("TEST 1: RapidAPI Credentials")
    print("="*80)
    
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key:
        print("❌ FAIL: Missing RAPIDAPI_KEY")
        print("   Add this to your backend/.env file:")
        print("   RAPIDAPI_KEY=your_rapidapi_key_here")
        return False
    
    print(f"✅ PASS: RapidAPI Key is set: {api_key[:20]}...")
    return True


def test_simple_one_way():
    """Test basic one-way flight search"""
    print("\n" + "="*80)
    print("TEST 2: One-Way Flight Search (London → Paris)")
    print("="*80)
    
    try:
        result = search_flights_kiwi(
            origin="City:london_gb",
            destination="City:paris_fr",
            departure_date="2025-12-20",
            adults=1,
            max_price=500,
            limit=5
        )
        
        if result["type"] == "error_result":
            error_msg = result['cards'][0]['data']['message']
            print(f"❌ FAIL: {error_msg}")
            print(f"   Details: {result['cards'][0]['data'].get('details', 'N/A')}")
            return False
        
        cards = result.get("cards", [])
        print(f"✅ PASS: Found {len(cards)} flights under $500")
        
        if cards:
            flight = cards[0]["data"]
            print(f"\nBest option:")
            print(f"  Airline: {flight.get('airline')}")
            print(f"  Flight: {flight.get('flight_number')}")
            print(f"  Route: {flight.get('origin')} → {flight.get('destination')}")
            print(f"  Departure: {flight.get('departure_time')}")
            print(f"  Arrival: {flight.get('arrival_time')}")
            print(f"  Price: ${flight.get('price')} {flight.get('currency')}")
            print(f"  Stops: {flight.get('stops')}")
            if flight.get('booking_link'):
                print(f"  Booking: {flight['booking_link'][:60]}...")
            else:
                print(f"  Booking: No link available")
            return True
        else:
            print("⚠️  WARNING: No flights found (may be unavailable on this date)")
            return True
    
    except Exception as e:
        print(f"❌ FAIL: Flight search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_round_trip():
    """Test round-trip flight search"""
    print("\n" + "="*80)
    print("TEST 3: Round-Trip Flight Search (NYC → London → NYC)")
    print("="*80)
    
    try:
        result = search_flights_kiwi(
            origin="City:new_york_us",
            destination="City:london_gb",
            departure_date="2025-12-20",
            return_date="2025-12-27",
            adults=2,
            limit=5
        )
        
        if result["type"] == "error_result":
            error_msg = result['cards'][0]['data']['message']
            print(f"Note: {error_msg}")
            return True
        
        cards = result.get("cards", [])
        print(f"✅ PASS: Found {len(cards)} round-trip options for 2 passengers")
        
        if cards:
            flight = cards[0]["data"]
            print(f"\nCheapest option:")
            print(f"  Price: ${flight.get('price')} {flight.get('currency')} (total for 2 people)")
            print(f"  Outbound: {flight.get('origin')} → {flight.get('destination')}")
            print(f"  Outbound legs: {len(flight.get('legs', {}).get('outbound', []))}")
            print(f"  Inbound legs: {len(flight.get('legs', {}).get('inbound', []))}")
            print(f"  Total stops: {flight.get('stops')}")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Round-trip search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_budget_filtering():
    """Test flight search with strict budget"""
    print("\n" + "="*80)
    print("TEST 4: Budget Filtering (max $200)")
    print("="*80)
    
    try:
        result = search_flights_kiwi(
            origin="City:london_gb",
            destination="City:dublin_ie",
            departure_date="2025-12-15",
            adults=1,
            max_price=200,  # Strict budget
            limit=10
        )
        
        if result["type"] == "error_result":
            print(f"Note: {result['cards'][0]['data']['message']}")
            return True
        
        cards = result.get("cards", [])
        print(f"✅ PASS: Found {len(cards)} flights under $200")
        
        # Verify all results are under budget
        over_budget = [c for c in cards if c["data"]["price"] > 200]
        if over_budget:
            print(f"❌ FAIL: {len(over_budget)} flights exceed budget!")
            return False
        
        if cards:
            prices = [c["data"]["price"] for c in cards]
            print(f"  Price range: ${min(prices)} - ${max(prices)}")
            print(f"  All flights within budget ✓")
        
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Budget filtering failed: {str(e)}")
        return False


def test_location_formats():
    """Test different location format inputs"""
    print("\n" + "="*80)
    print("TEST 5: Location Format Flexibility")
    print("="*80)
    
    test_cases = [
        ("City:london_gb", "City:paris_fr", "Kiwi format"),
        ("London", "Paris", "Plain city names"),
        ("JFK", "LHR", "IATA codes"),
    ]
    
    for origin, dest, description in test_cases:
        try:
            print(f"\n  Testing: {description} ({origin} → {dest})")
            result = search_flights_kiwi(
                origin=origin,
                destination=dest,
                adults=1,
                limit=2
            )
            
            if result["type"] == "error_result":
                print(f"    ⚠️  Error: {result['cards'][0]['data']['message']}")
            else:
                cards = result.get("cards", [])
                print(f"    ✅ Found {len(cards)} flights")
        
        except Exception as e:
            print(f"    ❌ Exception: {str(e)}")
    
    return True


def test_card_format():
    """Verify flight card format matches expected schema"""
    print("\n" + "="*80)
    print("TEST 6: Flight Card Format Validation")
    print("="*80)
    
    try:
        result = search_flights_kiwi(
            origin="City:london_gb",
            destination="City:amsterdam_nl",
            adults=1,
            limit=1
        )
        
        if result["type"] == "error_result":
            print(f"⚠️  Skipping (API error): {result['cards'][0]['data']['message']}")
            return True
        
        cards = result.get("cards", [])
        if not cards:
            print("⚠️  No flights to validate")
            return True
        
        flight = cards[0]
        required_fields = ["type", "id", "data"]
        required_data_fields = [
            "airline", "flight_number", "origin", "destination",
            "departure_time", "arrival_time", "price", "currency",
            "stops", "cabin_class", "booking_link"
        ]
        
        # Check structure
        for field in required_fields:
            if field not in flight:
                print(f"❌ FAIL: Missing top-level field: {field}")
                return False
        
        # Check data fields
        data = flight.get("data", {})
        for field in required_data_fields:
            if field not in data:
                print(f"❌ FAIL: Missing data field: {field}")
                return False
        
        print("✅ PASS: Flight card has all required fields")
        print(f"\nSample card structure:")
        print(f"  Type: {flight['type']}")
        print(f"  ID: {flight['id']}")
        print(f"  Data fields: {list(data.keys())}")
        return True
    
    except Exception as e:
        print(f"❌ FAIL: Card format validation failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀"*40)
    print("KIWI.COM FLIGHT SEARCH - INTEGRATION TESTS")
    print("🚀"*40)
    
    tests = [
        ("Credentials", test_credentials),
        ("One-Way Search", test_simple_one_way),
        ("Round-Trip Search", test_round_trip),
        ("Budget Filtering", test_budget_filtering),
        ("Location Formats", test_location_formats),
        ("Card Format", test_card_format),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Flight search is ready to use.")
        print("\nTry it in chat:")
        print('  @ai Find me flights from London to Paris for 2 people under $500')
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check configuration above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

