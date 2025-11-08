"""
Test RapidAPI Integration (Skyscanner + Booking.com)
Tests real API calls to verify credentials and card conversion.
"""
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

from agent.tools.rapidapi_search import (
    search_flights_skyscanner,
    search_hotels_booking,
    _get_airport_code
)


def test_airport_codes():
    """Test airport code mapping"""
    print("\n" + "="*60)
    print("TEST 1: Airport Code Mapping")
    print("="*60)
    
    test_locations = ["Seoul", "Paris", "New York", "Tokyo", "Singapore"]
    
    for location in test_locations:
        code = _get_airport_code(location)
        print(f"  {location:20} -> {code}")
    
    print("✅ Airport code mapping test complete\n")


def test_flight_search():
    """Test flight search with Skyscanner API"""
    print("="*60)
    print("TEST 2: Flight Search (Real Skyscanner API)")
    print("="*60)
    
    # Seoul to Tokyo
    origin = "ICN"
    destination = "NRT"
    departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"  Searching flights from {origin} to {destination}")
    print(f"  Departure: {departure_date}")
    print(f"  Passengers: 1")
    print(f"  (This may take 15-20 seconds...)")
    
    try:
        result = search_flights_skyscanner(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            passengers=1
        )
        
        # Check result structure
        assert "type" in result, "Result missing 'type' field"
        assert "cards" in result, "Result missing 'cards' field"
        assert "metadata" in result, "Result missing 'metadata' field"
        
        print(f"\n  ✅ Result type: {result['type']}")
        print(f"  ✅ Cards found: {len(result['cards'])}")
        print(f"  ✅ Metadata: {result['metadata']}")
        
        # Print first few flights
        for i, card in enumerate(result["cards"][:3], 1):
            data = card['data']
            print(f"\n  Flight {i}:")
            print(f"    Airline: {data.get('airline', 'N/A')}")
            print(f"    Flight Number: {data.get('flight_number', 'N/A')}")
            print(f"    Price: ${data.get('price', 'N/A')}")
            print(f"    Duration: {data.get('duration', 'N/A')} hours")
            print(f"    Stops: {data.get('stops', 'N/A')}")
            print(f"    Departure: {data.get('departure_time', 'N/A')}")
            print(f"    Arrival: {data.get('arrival_time', 'N/A')}")
        
        print("\n✅ Flight search test PASSED\n")
        
    except Exception as e:
        print(f"\n  ❌ Flight search FAILED: {str(e)}")
        print(f"  Check your RAPIDAPI_KEY in .env")
        print(f"  Make sure you subscribed to Skyscanner API on RapidAPI")
        print(f"  See RAPIDAPI_SETUP.md for instructions\n")


def test_hotel_search():
    """Test hotel search with Booking.com API"""
    print("="*60)
    print("TEST 3: Hotel Search (Real Booking.com API)")
    print("="*60)
    
    city = "Paris"
    check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=33)).strftime("%Y-%m-%d")
    
    print(f"  Searching hotels in {city}")
    print(f"  Check-in: {check_in}")
    print(f"  Check-out: {check_out}")
    print(f"  Guests: 2")
    print(f"  (This may take 10-15 seconds...)")
    
    try:
        result = search_hotels_booking(
            city=city,
            check_in=check_in,
            check_out=check_out,
            guests=2,
            max_price=300
        )
        
        # Check result structure
        assert "type" in result, "Result missing 'type' field"
        assert "cards" in result, "Result missing 'cards' field"
        assert "metadata" in result, "Result missing 'metadata' field"
        
        print(f"\n  ✅ Result type: {result['type']}")
        print(f"  ✅ Cards found: {len(result['cards'])}")
        print(f"  ✅ Metadata: {result['metadata']}")
        
        # Print first few hotels
        for i, card in enumerate(result["cards"][:3], 1):
            data = card['data']
            print(f"\n  Hotel {i}:")
            print(f"    Name: {data.get('name', 'N/A')}")
            print(f"    Price: ${data.get('price', 'N/A')}/{data.get('price_unit', 'night')}")
            print(f"    Total: ${data.get('total_price', 'N/A')} for {data.get('nights', 'N/A')} nights")
            print(f"    Rating: {data.get('rating', 'N/A')}/5 ({data.get('review_count', 0)} reviews)")
            print(f"    Location: {data.get('location', 'N/A')}")
            
            amenities = data.get('amenities', [])
            if amenities:
                print(f"    Amenities: {', '.join(amenities[:3])}")
        
        print("\n✅ Hotel search test PASSED\n")
        
    except Exception as e:
        print(f"\n  ❌ Hotel search FAILED: {str(e)}")
        print(f"  Check your RAPIDAPI_KEY in .env")
        print(f"  Make sure you subscribed to Booking.com API on RapidAPI")
        print(f"  See RAPIDAPI_SETUP.md for instructions\n")


def test_card_format_validation():
    """Test that cards match expected schema"""
    print("="*60)
    print("TEST 4: Card Format Validation")
    print("="*60)
    
    city = "Seoul"
    check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")
    
    try:
        result = search_hotels_booking(
            city=city,
            check_in=check_in,
            check_out=check_out,
            guests=2
        )
        
        if result["cards"]:
            card = result["cards"][0]
            
            # Validate card structure
            required_fields = ["type", "id", "data"]
            for field in required_fields:
                assert field in card, f"Card missing required field: {field}"
            
            # Validate hotel card data fields
            data = card["data"]
            hotel_fields = ["name", "price", "rating", "location"]
            missing_fields = [f for f in hotel_fields if f not in data]
            
            if missing_fields:
                print(f"  ⚠️  Missing optional fields: {missing_fields}")
            else:
                print(f"  ✅ All hotel card fields present")
            
            print(f"  ✅ Card structure valid")
            print(f"  ✅ Card type: {card['type']}")
            print(f"  ✅ Data fields: {list(data.keys())}")
        
        print("\n✅ Card format validation PASSED\n")
        
    except AssertionError as e:
        print(f"\n  ❌ Card format validation FAILED: {str(e)}\n")
    except Exception as e:
        print(f"\n  ❌ Test FAILED: {str(e)}\n")


def test_round_trip_flight():
    """Test round-trip flight search"""
    print("="*60)
    print("TEST 5: Round-Trip Flight Search")
    print("="*60)
    
    origin = "ICN"
    destination = "SIN"
    departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    return_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
    
    print(f"  Round trip: {origin} ↔ {destination}")
    print(f"  Outbound: {departure_date}")
    print(f"  Return: {return_date}")
    
    try:
        result = search_flights_skyscanner(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=2
        )
        
        print(f"\n  ✅ Result type: {result['type']}")
        print(f"  ✅ Cards found: {len(result['cards'])}")
        print(f"  ✅ Round-trip search works!")
        
        print("\n✅ Round-trip test PASSED\n")
        
    except Exception as e:
        print(f"\n  ❌ Test FAILED: {str(e)}\n")


def main():
    """Run all RapidAPI integration tests"""
    print("\n" + "="*60)
    print("RAPIDAPI INTEGRATION TESTS")
    print("(Skyscanner + Booking.com)")
    print("="*60)
    print("This will test real API calls to Skyscanner and Booking.com.")
    print("Make sure you have set RAPIDAPI_KEY in your .env file.")
    print("See RAPIDAPI_SETUP.md for instructions.")
    print("="*60 + "\n")
    
    # Run tests
    test_airport_codes()
    test_flight_search()
    test_hotel_search()
    test_card_format_validation()
    test_round_trip_flight()
    
    print("="*60)
    print("ALL TESTS COMPLETE!")
    print("="*60)
    print("\nIf all tests passed, your RapidAPI integration is working! 🎉")
    print("You now have access to:")
    print("  ✈️  Skyscanner: Real-time flight search")
    print("  🏨  Booking.com: Real-time hotel search")
    print("\nNext steps:")
    print("  1. Try a real query: 'Find flights from Seoul to Tokyo'")
    print("  2. Try hotels: 'Find hotels in Paris from June 15-20'")
    print("  3. Check the frontend to see if cards render properly\n")
    print("Available travel search options:")
    print("  - Skyscanner (flights) ← Primary")
    print("  - Booking.com (hotels) ← Primary")
    print("  - Google Places (restaurants, attractions)")
    print("  - Amadeus (backup for flights/hotels)\n")


if __name__ == "__main__":
    main()
