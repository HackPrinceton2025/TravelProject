"""
Google Maps API Integration for Places, Directions, and Transportation
"""
import os
import requests
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime


class GoogleMapsClient:
    """Client for Google Maps APIs (Places, Directions, etc.)"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")  # Same key works for all Google Maps APIs
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    # ============================================
    # Places API Methods
    # ============================================
    
    def nearby_search(
        self,
        location: str,
        radius: int = 5000,
        place_type: str = "restaurant",
        keyword: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Search for places near a location
        
        Args:
            location: Location as "lat,lng" or place name
            radius: Search radius in meters (max 50000)
            place_type: Type of place (restaurant, tourist_attraction, lodging, etc.)
            keyword: Additional search keyword
            min_rating: Minimum rating (1-5)
            max_results: Maximum number of results
            
        Returns:
            Dictionary with places data
        """
        # If location is not lat,lng, geocode it first
        if "," in location and location.replace(",", "").replace(".", "").replace("-", "").replace(" ", "").isdigit():
            location_coords = location
        else:
            location_coords = self._geocode_location(location)
        
        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            "location": location_coords,
            "radius": min(radius, 50000),
            "type": place_type,
            "key": self.api_key
        }
        
        if keyword:
            params["keyword"] = keyword
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                raise Exception(f"Google Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
            
            results = data.get("results", [])
            
            # Filter by rating if specified
            if min_rating:
                results = [r for r in results if r.get("rating", 0) >= min_rating]
            
            # Limit results
            results = results[:max_results]
            
            return {
                "status": data.get("status"),
                "results": results,
                "location": location_coords
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Google Places API request failed: {str(e)}")
    
    # ============================================
    # Directions API Methods
    # ============================================
    
    def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "transit",
        departure_time: Optional[str] = None,
        alternatives: bool = True,
        transit_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get directions between two locations
        
        Args:
            origin: Starting location (address or "lat,lng")
            destination: Ending location (address or "lat,lng")
            mode: Travel mode - "driving", "walking", "bicycling", "transit"
            departure_time: Departure time in ISO format (e.g., "2024-12-25T10:00:00")
            alternatives: Whether to return alternative routes
            transit_mode: Transit mode filter - "bus", "subway", "train", "tram", "rail"
            
        Returns:
            Dictionary with route information
        """
        url = f"{self.base_url}/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "alternatives": alternatives,
            "key": self.api_key
        }
        
        # Add departure time if specified (for transit mode)
        if departure_time:
            try:
                dt = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
                params["departure_time"] = int(dt.timestamp())
            except:
                # If parsing fails, use "now"
                params["departure_time"] = "now"
        elif mode == "transit":
            params["departure_time"] = "now"
        
        # Add transit mode filter if specified
        if transit_mode and mode == "transit":
            params["transit_mode"] = transit_mode
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                raise Exception(f"Google Directions API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Google Directions API request failed: {str(e)}")
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def _geocode_location(self, location_name: str) -> str:
        """
        Convert location name to lat,lng coordinates
        
        Args:
            location_name: Name of location (e.g., "Paris, France")
            
        Returns:
            Coordinates as "lat,lng" string
        """
        # Fallback coordinates for major cities
        fallback_coords = {
            "paris": "48.8566,2.3522",
            "london": "51.5074,-0.1278",
            "tokyo": "35.6762,139.6503",
            "new york": "40.7128,-74.0060",
            "los angeles": "34.0522,-118.2437",
            "seoul": "37.5665,126.9780",
            "bangkok": "13.7563,100.5018",
            "singapore": "1.3521,103.8198",
            "hong kong": "22.3193,114.1694",
            "dubai": "25.2048,55.2708",
            "rome": "41.9028,12.4964",
            "barcelona": "41.3851,2.1734",
            "amsterdam": "52.3676,4.9041",
            "berlin": "52.5200,13.4050",
            "madrid": "40.4168,-3.7038",
            "vienna": "48.2082,16.3738",
            "prague": "50.0755,14.4378",
            "istanbul": "41.0082,28.9784",
            "sydney": "-33.8688,151.2093",
            "melbourne": "-37.8136,144.9631",
            "toronto": "43.6532,-79.3832",
            "vancouver": "49.2827,-123.1207",
            "san francisco": "37.7749,-122.4194",
            "chicago": "41.8781,-87.6298",
            "boston": "42.3601,-71.0589",
            "miami": "25.7617,-80.1918"
        }
        
        # Check fallback first
        location_lower = location_name.lower().strip()
        for city, coords in fallback_coords.items():
            if city in location_lower:
                return coords
        
        # Try geocoding API
        url = f"{self.base_url}/geocode/json"
        params = {
            "address": location_name,
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "OK" and data.get("results"):
                location = data["results"][0]["geometry"]["location"]
                return f"{location['lat']},{location['lng']}"
            else:
                raise Exception(f"Geocoding failed for location: {location_name}")
            
        except Exception as e:
            raise Exception(f"Failed to geocode location '{location_name}': {str(e)}")
    
    def get_photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        """Get photo URL from photo reference"""
        return f"{self.base_url}/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={self.api_key}"
    
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a place including reviews and additional data
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Dictionary with detailed place information
        """
        url = f"{self.base_url}/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,rating,price_level,formatted_address,formatted_phone_number,website,opening_hours,reviews,types,photos,user_ratings_total,business_status",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") in ["OK", "ZERO_RESULTS"]:
                return data.get("result", {})
            else:
                # Return empty dict on error to avoid breaking the flow
                return {}
                
        except Exception as e:
            # Return empty dict on error
            return {}
    
    def extract_price_from_reviews(self, reviews: List[Dict[str, Any]]) -> Optional[str]:
        """
        Extract price information from reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Price hint extracted from reviews or None
        """
        if not reviews:
            return None
        
        price_keywords = [
            ("expensive", "💰💰💰 (Expensive)"),
            ("pricey", "💰💰💰 (Pricey)"),
            ("affordable", "💰 (Affordable)"),
            ("cheap", "💰 (Budget-friendly)"),
            ("reasonable", "💰💰 (Reasonable)"),
            ("moderate", "💰💰 (Moderate)"),
            ("budget", "💰 (Budget)"),
            ("luxury", "💰💰💰💰 (Luxury)"),
            ("high-end", "💰💰💰💰 (High-end)")
        ]
        
        # Check first 3 reviews for price mentions
        for review in reviews[:3]:
            text = review.get("text", "").lower()
            for keyword, price_hint in price_keywords:
                if keyword in text:
                    return price_hint
        
        return None


# Singleton instance
_maps_client = None

def get_maps_client() -> GoogleMapsClient:
    """Get or create GoogleMapsClient singleton"""
    global _maps_client
    if _maps_client is None:
        _maps_client = GoogleMapsClient()
    return _maps_client


# ============================================
# Agent Tool Functions - Places
# ============================================

def search_restaurants(
    location: str,
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_price_level: Optional[int] = None,
    radius: int = 5000
) -> Dict[str, Any]:
    """
    Search for restaurants in a location using Google Places API.
    
    Args:
        location: City name or "lat,lng" coordinates (e.g., "Paris, France" or "48.8566,2.3522")
        cuisine: Type of cuisine (e.g., "Italian", "Japanese", "Korean") - optional
        min_rating: Minimum rating 1-5 (e.g., 4.0 for highly rated) - optional
        max_price_level: Maximum price level 1-4 (1=cheap, 4=expensive) - optional
        radius: Search radius in meters, default 5000 (5km)
        
    Returns:
        Dictionary with restaurant cards in standardized format
    """
    try:
        client = get_maps_client()
        
        search_result = client.nearby_search(
            location=location,
            radius=radius,
            place_type="restaurant",
            keyword=cuisine,
            min_rating=min_rating,
            max_results=20
        )
        
        results = search_result.get("results", [])
        
        # Filter by price level if specified
        if max_price_level:
            results = [r for r in results if r.get("price_level", 1) <= max_price_level]
        
        # Convert to restaurant cards
        restaurant_cards = []
        for place in results[:15]:
            photo_url = None
            if place.get("photos"):
                photo_ref = place["photos"][0].get("photo_reference")
                if photo_ref:
                    photo_url = client.get_photo_url(photo_ref)
            
            # Get price level from nearby search
            price_level = place.get("price_level", 0)
            place_id = place.get("place_id")
            
            # If no price level, try to get more details
            price_info = None
            price_source = "API"
            website_url = None
            
            if price_level > 0:
                # Use standard price level
                price_info = "$" * price_level
            
            # Always try to get details for website and better price info
            if place_id:
                details = client.get_place_details(place_id)
                
                # Get website URL
                website_url = details.get("website")
                
                # Update price info if not set
                if not price_info:
                    # Check if details have price_level
                    detail_price = details.get("price_level", 0)
                    if detail_price > 0:
                        price_info = "$" * detail_price
                        price_source = "Details API"
                    else:
                        # Extract from reviews
                        reviews = details.get("reviews", [])
                        review_price = client.extract_price_from_reviews(reviews)
                        if review_price:
                            price_info = review_price
                            price_source = "Reviews"
                        else:
                            price_info = "💬 Contact for pricing"
            
            types = place.get("types", [])
            cuisine_types = [t.replace("_", " ").title() for t in types if t not in ["restaurant", "food", "point_of_interest", "establishment"]]
            
            restaurant_cards.append({
                "type": "restaurant",
                "id": f"restaurant_{uuid.uuid4().hex[:8]}",
                "data": {
                    "name": place.get("name", "Unknown Restaurant"),
                    "cuisine": cuisine_types[0] if cuisine_types else "Restaurant",
                    "rating": place.get("rating", 0),
                    "price_level": price_info,
                    "price_source": price_source,  # Indicates where price info came from
                    "address": place.get("vicinity", "Address not available"),
                    "website": website_url,  # Restaurant website URL
                    "image": photo_url,
                    "open_now": place.get("opening_hours", {}).get("open_now"),
                    "total_ratings": place.get("user_ratings_total", 0),
                    "place_id": place.get("place_id"),
                    "location": {
                        "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                        "lng": place.get("geometry", {}).get("location", {}).get("lng")
                    }
                }
            })
        
        return {
            "type": "restaurant_search_result",
            "cards": restaurant_cards,
            "metadata": {
                "source": "Google Places API",
                "query_location": location,
                "cuisine": cuisine,
                "min_rating": min_rating,
                "total_results": len(restaurant_cards)
            }
        }
    
    except Exception as e:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to search restaurants: {str(e)}",
                    "error_type": "api_error"
                }
            }],
            "metadata": {"error": str(e)}
        }


def search_attractions(
    location: str,
    attraction_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    radius: int = 10000
) -> Dict[str, Any]:
    """
    Search for tourist attractions in a location using Google Places API.
    
    Args:
        location: City name or "lat,lng" coordinates (e.g., "Paris, France" or "48.8566,2.3522")
        attraction_type: Type of attraction (e.g., "museum", "park", "landmark") - optional
        min_rating: Minimum rating 1-5 (e.g., 4.0 for highly rated) - optional
        radius: Search radius in meters, default 10000 (10km)
        
    Returns:
        Dictionary with attraction cards in standardized format
    """
    try:
        client = get_maps_client()
        
        search_result = client.nearby_search(
            location=location,
            radius=radius,
            place_type="tourist_attraction",
            keyword=attraction_type,
            min_rating=min_rating,
            max_results=20
        )
        
        results = search_result.get("results", [])
        
        # Convert to attraction cards
        attraction_cards = []
        for place in results[:15]:
            photo_url = None
            if place.get("photos"):
                photo_ref = place["photos"][0].get("photo_reference")
                if photo_ref:
                    photo_url = client.get_photo_url(photo_ref)
            
            # Get website from place details
            place_id = place.get("place_id")
            website_url = None
            if place_id:
                details = client.get_place_details(place_id)
                website_url = details.get("website")
            
            types = place.get("types", [])
            category_types = [t.replace("_", " ").title() for t in types if t not in ["tourist_attraction", "point_of_interest", "establishment"]]
            
            attraction_cards.append({
                "type": "attraction",
                "id": f"attraction_{uuid.uuid4().hex[:8]}",
                "data": {
                    "name": place.get("name", "Unknown Attraction"),
                    "category": category_types[0] if category_types else "Tourist Attraction",
                    "rating": place.get("rating", 0),
                    "description": place.get("vicinity", ""),
                    "address": place.get("vicinity", "Address not available"),
                    "website": website_url,  # Attraction website URL
                    "image": photo_url,
                    "open_now": place.get("opening_hours", {}).get("open_now"),
                    "total_ratings": place.get("user_ratings_total", 0),
                    "place_id": place.get("place_id"),
                    "location": {
                        "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                        "lng": place.get("geometry", {}).get("location", {}).get("lng")
                    }
                }
            })
        
        return {
            "type": "attraction_search_result",
            "cards": attraction_cards,
            "metadata": {
                "source": "Google Places API",
                "query_location": location,
                "attraction_type": attraction_type,
                "min_rating": min_rating,
                "total_results": len(attraction_cards)
            }
        }
    
    except Exception as e:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to search attractions: {str(e)}",
                    "error_type": "api_error"
                }
            }],
            "metadata": {"error": str(e)}
        }


def search_hotels(
    location: str,
    min_rating: Optional[float] = None,
    max_price_level: Optional[int] = None,
    radius: int = 5000
) -> Dict[str, Any]:
    """
    Search for hotels in a location using Google Places API.
    
    Args:
        location: City name or "lat,lng" coordinates (e.g., "Paris, France" or "48.8566,2.3522")
        min_rating: Minimum rating 1-5 (e.g., 4.0 for highly rated) - optional
        max_price_level: Maximum price level 1-4 (1=cheap, 4=expensive) - optional
        radius: Search radius in meters, default 5000 (5km)
        
    Returns:
        Dictionary with hotel cards in standardized format
    """
    try:
        client = get_maps_client()
        
        search_result = client.nearby_search(
            location=location,
            radius=radius,
            place_type="lodging",
            min_rating=min_rating,
            max_results=20
        )
        
        results = search_result.get("results", [])
        
        # Filter by price level if specified
        if max_price_level:
            results = [r for r in results if r.get("price_level", 1) <= max_price_level]
        
        # Convert to hotel cards
        hotel_cards = []
        for place in results[:15]:
            photo_url = None
            if place.get("photos"):
                photo_ref = place["photos"][0].get("photo_reference")
                if photo_ref:
                    photo_url = client.get_photo_url(photo_ref)
            
            # Get price level from nearby search
            price_level = place.get("price_level", 0)
            place_id = place.get("place_id")
            
            # If no price level, try to get more details
            price_info = None
            price_source = "API"
            website_url = None
            
            if price_level > 0:
                # Use standard price level
                price_info = "$" * price_level
            
            # Always try to get details for website and better price info
            if place_id:
                details = client.get_place_details(place_id)
                
                # Get website URL
                website_url = details.get("website")
                
                # Update price info if not set
                if not price_info:
                    # Check if details have price_level
                    detail_price = details.get("price_level", 0)
                    if detail_price > 0:
                        price_info = "$" * detail_price
                        price_source = "Details API"
                    else:
                        # Extract from reviews
                        reviews = details.get("reviews", [])
                        review_price = client.extract_price_from_reviews(reviews)
                        if review_price:
                            price_info = review_price
                            price_source = "Reviews"
                        else:
                            price_info = "🔍 Check website for rates"
            
            hotel_cards.append({
                "type": "hotel",
                "id": f"hotel_{uuid.uuid4().hex[:8]}",
                "data": {
                    "name": place.get("name", "Unknown Hotel"),
                    "rating": place.get("rating", 0),
                    "price": price_info,
                    "price_source": price_source,
                    "price_unit": "per night",
                    "address": place.get("vicinity", "Address not available"),
                    "website": website_url,  # Hotel website URL
                    "image": photo_url,
                    "total_ratings": place.get("user_ratings_total", 0),
                    "place_id": place.get("place_id"),
                    "location": {
                        "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                        "lng": place.get("geometry", {}).get("location", {}).get("lng")
                    }
                }
            })
        
        return {
            "type": "hotel_search_result",
            "cards": hotel_cards,
            "metadata": {
                "source": "Google Places API",
                "query_location": location,
                "min_rating": min_rating,
                "total_results": len(hotel_cards)
            }
        }
    
    except Exception as e:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to search hotels: {str(e)}",
                    "error_type": "api_error"
                }
            }],
            "metadata": {"error": str(e)}
        }


# ============================================
# Agent Tool Functions - Directions/Transportation
# ============================================

def search_transportation(
    origin: str,
    destination: str,
    mode: str = "transit",
    departure_time: Optional[str] = None,
    transit_mode: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for transportation options between two locations using Google Directions API.
    Supports multiple travel modes including transit, driving, walking, and bicycling.
    
    Args:
        origin: Starting location (city name, address, or "lat,lng")
        destination: Ending location (city name, address, or "lat,lng")
        mode: Travel mode - "transit" (public transport), "driving" (car), "walking", or "bicycling"
        departure_time: Departure time in ISO format (e.g., "2024-12-25T10:00:00") - optional
        transit_mode: Transit type filter - "bus", "subway", "train", "tram", "rail" - optional (only for transit mode)
        
    Returns:
        Dictionary with transportation cards showing different route options
    """
    try:
        client = get_maps_client()
        
        # Get directions
        directions_data = client.get_directions(
            origin=origin,
            destination=destination,
            mode=mode,
            departure_time=departure_time,
            alternatives=True,
            transit_mode=transit_mode
        )
        
        routes = directions_data.get("routes", [])
        
        if not routes:
            return {
                "type": "transportation_search_result",
                "cards": [],
                "metadata": {
                    "source": "Google Directions API",
                    "message": f"No routes found from {origin} to {destination}",
                    "mode": mode
                }
            }
        
        # Convert to transportation cards
        transport_cards = []
        for route in routes[:5]:  # Limit to 5 routes
            leg = route["legs"][0]  # Use first leg
            
            # Calculate duration and distance
            duration_seconds = leg["duration"]["value"]
            duration_hours = round(duration_seconds / 3600, 1)
            distance_meters = leg["distance"]["value"]
            distance_km = round(distance_meters / 1000, 1)
            
            # Get departure and arrival times
            departure_time_str = leg.get("departure_time", {}).get("text", "N/A")
            arrival_time_str = leg.get("arrival_time", {}).get("text", "N/A")
            
            # Build route description based on mode
            if mode == "transit":
                # Extract transit details
                steps = leg.get("steps", [])
                transit_steps = [s for s in steps if s.get("travel_mode") == "TRANSIT"]
                
                route_description = []
                vehicle_types = []
                
                for step in transit_steps:
                    transit_details = step.get("transit_details", {})
                    line = transit_details.get("line", {})
                    vehicle = line.get("vehicle", {})
                    vehicle_type = vehicle.get("type", "Transit")
                    vehicle_name = line.get("short_name") or line.get("name", "Unknown")
                    
                    vehicle_types.append(vehicle_type)
                    route_description.append(f"{vehicle_type}: {vehicle_name}")
                
                # Create card
                transport_cards.append({
                    "type": "transportation",
                    "id": f"transport_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "mode": "Transit",
                        "origin": origin,
                        "destination": destination,
                        "departure_time": departure_time_str,
                        "arrival_time": arrival_time_str,
                        "duration": duration_hours,
                        "distance": distance_km,
                        "route_description": " → ".join(route_description),
                        "vehicle_types": list(set(vehicle_types)),
                        "steps": len(transit_steps),
                        "price": "Varies",  # Google doesn't provide fare info
                        "currency": "USD"
                    }
                })
            
            elif mode == "driving":
                transport_cards.append({
                    "type": "transportation",
                    "id": f"transport_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "mode": "Driving",
                        "origin": origin,
                        "destination": destination,
                        "departure_time": departure_time_str if departure_time_str != "N/A" else "Flexible",
                        "arrival_time": arrival_time_str if arrival_time_str != "N/A" else "Flexible",
                        "duration": duration_hours,
                        "distance": distance_km,
                        "route_description": f"Drive via {route.get('summary', 'main roads')}",
                        "price": "Self-drive",
                        "currency": "USD"
                    }
                })
            
            elif mode == "walking":
                transport_cards.append({
                    "type": "transportation",
                    "id": f"transport_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "mode": "Walking",
                        "origin": origin,
                        "destination": destination,
                        "duration": duration_hours,
                        "distance": distance_km,
                        "route_description": f"Walk {distance_km}km",
                        "price": "Free",
                        "currency": "USD"
                    }
                })
            
            elif mode == "bicycling":
                transport_cards.append({
                    "type": "transportation",
                    "id": f"transport_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "mode": "Bicycling",
                        "origin": origin,
                        "destination": destination,
                        "duration": duration_hours,
                        "distance": distance_km,
                        "route_description": f"Bike {distance_km}km",
                        "price": "Free",
                        "currency": "USD"
                    }
                })
        
        return {
            "type": "transportation_search_result",
            "cards": transport_cards,
            "metadata": {
                "source": "Google Directions API",
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "total_results": len(transport_cards)
            }
        }
    
    except Exception as e:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to search transportation: {str(e)}",
                    "error_type": "api_error"
                }
            }],
            "metadata": {"error": str(e)}
        }
