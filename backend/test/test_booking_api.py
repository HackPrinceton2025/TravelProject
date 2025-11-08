"""
Test Booking.com API Integration (Flights + Hotels)
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.tools.rapidapi_search import (
    search_flights_booking,
    search_hotels_booking,
    get_booking_client
)


def test_flight_destination_search():
    """Test flight destination/airport search"""
    print("\n" + "="*80)
    print("TEST: Flight Destination Search")
    print("="*80)
    
    client = get_booking_client()
    
    test_queries = ["New York", "Paris", "Seoul", "Tokyo", "London"]
    
    for query in test_queries:
        try:
            result = client.search_flight_destination(query)
            if result.get("data"):
                airport = result["data"][0]
                print(f"\n✈️  {query}")
                print(f"   ID: {airport['id']}")
                print(f"   Name: {airport['name']}")
                print(f"   Type: {airport.get('type', 'N/A')}")
            else:
                print(f"\n⚠️  {query}: No data found")
        except Exception as e:
            print(f"\n❌ {query}: {str(e)}")


def test_raw_api_response():
    """Test raw API response structure"""
    print("\n" + "="*80)
    print("TEST: Raw API Response Structure")
    print("="*80)
    
    client = get_booking_client()
    
    try:
        # Test Flight API
        print("\n--- FLIGHT API ---")
        origin_data = client.search_flight_destination("New York City")
        dest_data = client.search_flight_destination("Atlanta")
        
        if not origin_data.get("data") or not dest_data.get("data"):
            print("❌ Could not find origin or destination")
            return
        
        from_id = origin_data["data"][0]["id"]
        to_id = dest_data["data"][0]["id"]
        
        print(f"\nOrigin ID: {from_id}")
        print(f"Destination ID: {to_id}")
        
        # Make flight search
        response = client.search_flights(
            from_id=from_id,
            to_id=to_id,
            depart_date="2025-11-15",
            adults=1,
            cabin_class="ECONOMY",
            stops="none"
        )
        
        print(f"\nAPI Status: {response.get('status')}")
        print(f"Message: {response.get('message')}")
        
        if response.get("data"):
            data = response["data"]
            print(f"\nData keys: {list(data.keys())}")
            
            if data.get("flightOffers"):
                print(f"Total flight offers: {len(data['flightOffers'])}")
                
                # Show first offer structure
                if data["flightOffers"]:
                    first_offer = data["flightOffers"][0]
                    print(f"\nFirst offer keys: {list(first_offer.keys())}")
                    
                    if first_offer.get("segments"):
                        print(f"Number of segments: {len(first_offer['segments'])}")
                        first_segment = first_offer["segments"][0]
                        print(f"First segment keys: {list(first_segment.keys())}")
                        
                        if first_segment.get("legs"):
                            print(f"Number of legs in first segment: {len(first_segment['legs'])}")
                            first_leg = first_segment["legs"][0]
                            print(f"First leg keys: {list(first_leg.keys())}")
                    
                    if first_offer.get("priceBreakdown"):
                        price_breakdown = first_offer["priceBreakdown"]
                        print(f"\nPrice breakdown keys: {list(price_breakdown.keys())}")
                        if price_breakdown.get("total"):
                            total = price_breakdown["total"]
                            print(f"Total price: {total.get('units', 0)} + {total.get('nanos', 0)/1_000_000_000:.2f} {total.get('currencyCode', 'USD')}")
            
            if data.get("aggregation"):
                agg = data["aggregation"]
                print(f"\nAggregation total count: {agg.get('totalCount', 0)}")
                print(f"Min price: {agg.get('minPrice', {})}")
        
        # Test Hotel API
        print("\n\n--- HOTEL API ---")
        hotel_response = client.search_hotels_booking(
            city_name="Philadelphia",
            check_in="2025-11-15",
            check_out="2025-11-18",
            adults=2,
            rooms=1
        )
        
        print(f"\nHotel API Status: {hotel_response.get('status')}")
        print(f"Message: {hotel_response.get('message', 'N/A')}")
        
        if hotel_response.get("data"):
            data = hotel_response["data"]
            print(f"\nHotel data keys: {list(data.keys())}")
            
            # Check different possible keys for hotel list
            if "hotels" in data:
                print(f"Found 'hotels' key with {len(data['hotels'])} hotels")
            elif "result" in data:
                print(f"Found 'result' key")
                result = data["result"]
                if isinstance(result, list):
                    print(f"Result is list with {len(result)} items")
                elif isinstance(result, dict):
                    print(f"Result is dict with keys: {list(result.keys())}")
            elif "properties" in data:
                print(f"Found 'properties' key with {len(data['properties'])} properties")
            else:
                print(f"No expected hotel list key found. Available keys: {list(data.keys())}")
            
            # Show first hotel structure if available
            hotels = data.get("hotels") or data.get("properties") or data.get("result", [])
            if hotels and isinstance(hotels, list) and len(hotels) > 0:
                first_hotel = hotels[0]
                print(f"\nFirst hotel keys: {list(first_hotel.keys())}")
                
                # Check property structure
                if first_hotel.get("property"):
                    prop = first_hotel["property"]
                    print(f"Property keys: {list(prop.keys())}")
                    
                    if prop.get("priceBreakdown"):
                        print(f"Price breakdown keys: {list(prop['priceBreakdown'].keys())}")
                    if prop.get("reviewScore"):
                        print(f"Review score: {prop.get('reviewScore')}")
                    if prop.get("reviewScoreWord"):
                        print(f"Review word: {prop.get('reviewScoreWord')}")
                        
                elif first_hotel.get("priceBreakdown"):
                    print(f"Price breakdown keys: {list(first_hotel['priceBreakdown'].keys())}")
        else:
            print("\n⚠️  No data in hotel response")
            print(f"Full response keys: {list(hotel_response.keys())}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


def test_search_flights():
    """Test flight search"""
    print("\n" + "="*80)
    print("TEST: Flight Search - New York to Paris")
    print("="*80)
    
    result = search_flights_booking(
        origin="New York",
        destination="Paris",
        departure_date="2025-11-15",
        passengers=1,
        cabin_class="ECONOMY",
        max_stops="none"  # Direct flights only
    )
    
    print(f"\nResult Type: {result['type']}")
    print(f"Source: {result['metadata'].get('source', 'Unknown')}")
    print(f"Total Results: {result['metadata'].get('total_results', 0)}")
    
    if result.get('metadata', {}).get('query'):
        print(f"Query: {result['metadata']['query']}")
    
    # Check for error
    if result['type'] == 'error_result':
        print(f"\n❌ Error: {result['cards'][0]['data']['message']}")
        return
    
    if result['cards']:
        print("\n--- First 3 Flights ---")
        for card in result['cards'][:3]:
            data = card['data']
            print(f"\n✈️  {data['airline']}")
            if data.get('airline_logo'):
                print(f"   Logo: {data['airline_logo'][:60]}...")
            print(f"   Flight: {data['flight_number']}")
            print(f"   Route: {data['origin']} → {data['destination']}")
            print(f"   Departure: {data['departure_time']}")
            print(f"   Arrival: {data['arrival_time']}")
            print(f"   Duration: {data['duration']} hours")
            print(f"   Price: ${data['price']} {data['currency']}")
            print(f"   Stops: {data['stops']}")
            print(f"   Class: {data['cabin_class']}")
            if data.get('booking_token'):
                print(f"   Token: {data['booking_token'][:50]}...")
    else:
        print("\n⚠️  No flights found")


def test_search_hotels():
    """Test hotel search"""
    print("\n" + "="*80)
    print("TEST: Hotel Search - New York City")
    print("="*80)
    
    result = search_hotels_booking(
        city="New York City",
        check_in="2025-11-15",
        check_out="2025-11-18",
        max_price=300,
        guests=2,
        rooms=1,
        min_rating=7.5
    )
    
    print(f"\nResult Type: {result['type']}")
    print(f"Total Results: {result['metadata'].get('total_results', 0)}")
    
    # Check for error
    if result['type'] == 'error_result':
        print(f"\n❌ Error: {result['cards'][0]['data']['message']}")
        return
    
    if result['cards']:
        print("\n--- First 3 Hotels ---")
        for card in result['cards'][:3]:
            data = card['data']
            print(f"\n🏨  {data['name']}")
            if data.get('stars'):
                print(f"   Stars: {'⭐' * int(data['stars'])}")
            print(f"   Rating: {data['rating']}/5 ({data['review_score']}/10) - {data.get('review_score_word', '')}")
            print(f"   Reviews: {data['review_count']}")
            print(f"   Price: ${data['price']}/{data['price_unit']} ({data['currency']})")
            print(f"   Total: ${data['total_price']} for {data['nights']} nights")
            if data.get('location'):
                print(f"   Location: {data['location']}")
            if data.get('country_code'):
                print(f"   Country: {data['country_code']}")
            if data.get('is_preferred'):
                print(f"   ⭐ Preferred Property")
            if data.get('image'):
                print(f"   Image: {data['image'][:60]}...")
    else:
        print("\n⚠️  No hotels found")


def test_round_trip_flight():
    """Test round trip flight search"""
    print("\n" + "="*80)
    print("TEST: Round Trip Flight - Seoul to Tokyo")
    print("="*80)
    
    result = search_flights_booking(
        origin="Seoul",
        destination="Tokyo",
        departure_date="2025-11-20",
        return_date="2025-11-27",
        passengers=2,
        cabin_class="ECONOMY"
    )
    
    print(f"\nResult Type: {result['type']}")
    print(f"Total Results: {result['metadata'].get('total_results', 0)}")
    
    # Check for error
    if result['type'] == 'error_result':
        print(f"\n❌ Error: {result['cards'][0]['data']['message']}")
        return
    
    if result['cards']:
        print("\n--- Round Trip Flights ---")
        for card in result['cards'][:2]:
            data = card['data']
            print(f"\n✈️  {data['airline']} - {data['flight_number']}")
            print(f"   Outbound: {data['departure_date']}")
            print(f"   Return: {data.get('return_date', 'N/A')}")
            print(f"   Price: ${data['price']} {data['currency']} total")
            print(f"   Duration: {data['duration']} hours")
            print(f"   Stops: {data['stops']}")
    else:
        print("\n⚠️  No flights found")


def test_business_class_flight():
    """Test business class flight search"""
    print("\n" + "="*80)
    print("TEST: Business Class Flight - Los Angeles to London")
    print("="*80)
    
    result = search_flights_booking(
        origin="Los Angeles",
        destination="London",
        departure_date="2025-11-25",
        passengers=1,
        cabin_class="BUSINESS",
        max_price=5000
    )
    
    print(f"\nResult Type: {result['type']}")
    print(f"Total Results: {result['metadata'].get('total_results', 0)}")
    print(f"Cabin Class: {result['metadata'].get('cabin_class', 'N/A')}")
    
    # Check for error
    if result['type'] == 'error_result':
        print(f"\n❌ Error: {result['cards'][0]['data']['message']}")
        return
    
    if result['cards']:
        print("\n--- Business Class Flights ---")
        for card in result['cards'][:2]:
            data = card['data']
            print(f"\n✈️  {data['airline']}")
            print(f"   Price: ${data['price']} {data['currency']}")
            print(f"   Duration: {data['duration']} hours")
            print(f"   Class: {data['cabin_class']}")
    else:
        print("\n⚠️  No flights found")


if __name__ == "__main__":
    try:
        # Test destination search
        # test_flight_destination_search()
        
        # Test raw API response structure (for debugging)
        # test_raw_api_response()
        
        # Test flight searches
        # test_search_flights()
        # test_round_trip_flight()
        # test_business_class_flight()
        
        # Test hotel search
        test_search_hotels()
        
        print("\n" + "="*80)
        print("✅ All Booking.com API tests completed!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
