"""
Test Google Maps API Integration (Places + Directions)
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.tools.google_maps import (
    search_restaurants,
    search_attractions,
    search_hotels,
    search_transportation,
    get_maps_client
)


def test_search_restaurants():
    """Test restaurant search"""
    print("\n" + "="*80)
    print("TEST: Restaurant Search in Paris")
    print("="*80)
    
    result = search_restaurants(
        location="Paris, France",
        cuisine="French",
        min_rating=4.0,
        max_price_level=3,
        radius=3000
    )
    
    print(f"\nResult Type: {result['type']}")
    print(f"Total Results: {result['metadata']['total_results']}")
    print(f"Source: {result['metadata']['source']}")
    
    if result['cards']:
        print("\n--- First 3 Restaurants ---")
        for card in result['cards'][:3]:
            data = card['data']
            print(f"\n🍽️  {data['name']}")
            print(f"   Cuisine: {data['cuisine']}")
            print(f"   Rating: {data['rating']} ⭐ ({data['total_ratings']} reviews)")
            print(f"   Price: {data['price_level']} (Source: {data.get('price_source', 'Unknown')})")
            print(f"   Address: {data['address']}")
            print(f"   Open Now: {data.get('open_now', 'Unknown')}")
            if data.get('image'):
                print(f"   Image: {data['image'][:60]}...")
        
        # Price statistics
        price_sources = {}
        for card in result['cards']:
            source = card['data'].get('price_source', 'Unknown')
            price_sources[source] = price_sources.get(source, 0) + 1
        
        print("\n--- Price Information Statistics ---")
        for source, count in price_sources.items():
            print(f"   {source}: {count} restaurants")


def test_search_attractions():
    """Test attraction search"""
    print("\n" + "="*80)
    print("TEST: Attraction Search in Tokyo")
    print("="*80)
    
    result = search_attractions(
        location="Tokyo, Japan",
        attraction_type="temple",
        min_rating=4.2,
        radius=8000
    )
    
    print(f"\nResult Type: {result['type']}")
    print(f"Total Results: {result['metadata']['total_results']}")
    
    if result['cards']:
        print("\n--- First 3 Attractions ---")
        for card in result['cards'][:3]:
            data = card['data']
            print(f"\n🏯  {data['name']}")
            print(f"   Category: {data['category']}")
            print(f"   Rating: {data['rating']} ⭐ ({data['total_ratings']} reviews)")
            print(f"   Address: {data['address']}")


def test_search_hotels():
    """Test hotel search"""
    print("\n" + "="*80)
    print("TEST: Hotel Search in Seoul")
    print("="*80)
    
    result = search_hotels(
        location="Seoul, South Korea",
        min_rating=4.0,
        max_price_level=3,
        radius=5000
    )
    
    print(f"\nResult Type: {result['type']}")
    print(f"Total Results: {result['metadata']['total_results']}")
    
    if result['cards']:
        print("\n--- First 3 Hotels ---")
        for card in result['cards'][:3]:
            data = card['data']
            print(f"\n🏨  {data['name']}")
            print(f"   Rating: {data['rating']} ⭐ ({data['total_ratings']} reviews)")
            print(f"   Price: {data['price']} {data['price_unit']} (Source: {data.get('price_source', 'Unknown')})")
            print(f"   Address: {data['address']}")
        
        # Price statistics
        price_sources = {}
        for card in result['cards']:
            source = card['data'].get('price_source', 'Unknown')
            price_sources[source] = price_sources.get(source, 0) + 1
        
        print("\n--- Price Information Statistics ---")
        for source, count in price_sources.items():
            print(f"   {source}: {count} hotels")


def test_transit_search():
    """Test public transit search"""
    print("\n" + "="*80)
    print("TEST: Public Transit from Paris to Lyon")
    print("="*80)
    
    result = search_transportation(
        origin="Paris, France",
        destination="Lyon, France",
        mode="transit",
        transit_mode="train"
    )
    
    print(f"\nResult Type: {result['type']}")
    print(f"Total Results: {result['metadata']['total_results']}")
    print(f"Mode: {result['metadata']['mode']}")
    
    if result['cards']:
        print("\n--- Transportation Options ---")
        for card in result['cards']:
            data = card['data']
            print(f"\n🚆  {data['mode']}")
            print(f"   Route: {data['origin']} → {data['destination']}")
            print(f"   Departure: {data.get('departure_time', 'N/A')}")
            print(f"   Arrival: {data.get('arrival_time', 'N/A')}")
            print(f"   Duration: {data['duration']} hours")
            print(f"   Distance: {data['distance']} km")
            if data.get('route_description'):
                print(f"   Route: {data['route_description']}")
            print(f"   Price: {data['price']}")


def test_driving_search():
    """Test driving directions"""
    print("\n" + "="*80)
    print("TEST: Driving from San Francisco to Los Angeles")
    print("="*80)
    
    result = search_transportation(
        origin="San Francisco, CA",
        destination="Los Angeles, CA",
        mode="driving"
    )
    
    print(f"\nResult Type: {result['type']}")
    print(f"Total Results: {result['metadata']['total_results']}")
    
    if result['cards']:
        print("\n--- Driving Routes ---")
        for card in result['cards']:
            data = card['data']
            print(f"\n🚗  {data['mode']}")
            print(f"   Duration: {data['duration']} hours")
            print(f"   Distance: {data['distance']} km")
            print(f"   Route: {data.get('route_description', 'N/A')}")


def test_walking_search():
    """Test walking directions"""
    print("\n" + "="*80)
    print("TEST: Walking in Central Park")
    print("="*80)
    
    result = search_transportation(
        origin="Central Park South, New York, NY",
        destination="Bethesda Terrace, Central Park, NY",
        mode="walking"
    )
    
    print(f"\nResult Type: {result['type']}")
    
    if result['cards']:
        card = result['cards'][0]
        data = card['data']
        print(f"\n🚶  {data['mode']}")
        print(f"   Duration: {data['duration']} hours")
        print(f"   Distance: {data['distance']} km")
        print(f"   Route: {data['route_description']}")


def test_client_geocoding():
    """Test geocoding functionality"""
    print("\n" + "="*80)
    print("TEST: Geocoding Various Locations")
    print("="*80)
    
    client = get_maps_client()
    
    test_locations = [
        "Paris, France",
        "Tokyo, Japan",
        "New York, USA",
        "Sydney, Australia",
        "Seoul, South Korea"
    ]
    
    for location in test_locations:
        try:
            coords = client._geocode_location(location)
            print(f"\n📍 {location}")
            print(f"   Coordinates: {coords}")
        except Exception as e:
            print(f"\n❌ {location}")
            print(f"   Error: {str(e)}")


if __name__ == "__main__":
    try:
        # Test Places API
        test_search_restaurants()
        test_search_attractions()
        test_search_hotels()
        
        # Test Directions API
        test_transit_search()
        test_driving_search()
        test_walking_search()
        
        # Test Geocoding
        test_client_geocoding()
        
        print("\n" + "="*80)
        print("✅ All Google Maps API tests completed!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
