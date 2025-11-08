"""
RapidAPI Integration for Flight and Hotel Search
Uses Booking.com API for both flights and hotels
"""
import os
import requests
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timedelta


class BookingAPIClient:
    """Client for Booking.com API (flights + hotels)"""
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.base_url = "https://booking-com15.p.rapidapi.com/api/v1"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }
    
    def search_flight_destination(self, query: str) -> Dict[str, Any]:
        """
        Search for flight destination/airport ID
        
        Args:
            query: City or airport name
            
        Returns:
            Destination data with airport IDs
        """
        url = f"{self.base_url}/flights/searchDestination"
        params = {"query": query}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Booking.com destination search failed: {str(e)}")
    
    def search_flights(
        self,
        from_id: str,
        to_id: str,
        depart_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        children: str = "",
        cabin_class: str = "ECONOMY",
        stops: str = "none",
        currency: str = "USD",
        page_no: int = 1
    ) -> Dict[str, Any]:
        """
        Search flights using Booking.com API
        
        Args:
            from_id: Origin airport ID (e.g., "JFK.AIRPORT")
            to_id: Destination airport ID (e.g., "CDG.AIRPORT")
            depart_date: Departure date (YYYY-MM-DD)
            return_date: Return date for round trip (optional)
            adults: Number of adult passengers
            children: Children ages (e.g., "0,17" for 2 children)
            cabin_class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
            stops: "none", "1", "2+"
            currency: Currency code
            page_no: Page number for pagination
            
        Returns:
            Flight data from Booking.com
        """
        url = f"{self.base_url}/flights/searchFlights"
        
        params = {
            "fromId": from_id,
            "toId": to_id,
            "departDate": depart_date,
            "stops": stops,
            "pageNo": str(page_no),
            "adults": str(adults),
            "children": children,
            "sort": "BEST",
            "cabinClass": cabin_class,
            "currency_code": currency
        }
        
        if return_date:
            params["returnDate"] = return_date
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Booking.com flights search failed: {str(e)}")
    
    def search_hotels_booking(
        self,
        city_name: str,
        check_in: str,
        check_out: str,
        adults: int = 2,
        rooms: int = 1,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Search hotels using Booking.com API
        
        Args:
            city_name: City name (e.g., "Paris", "New York")
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            adults: Number of adults
            rooms: Number of rooms
            currency: Currency code
            
        Returns:
            Hotel data from Booking.com
        """
        # Step 1: Search for destination ID
        dest_url = f"{self.base_url}/hotels/searchDestination"
        dest_params = {"query": city_name}
        
        try:
            dest_response = requests.get(dest_url, headers=self.headers, params=dest_params, timeout=30)
            dest_response.raise_for_status()
            dest_data = dest_response.json()
            
            if not dest_data.get("data"):
                raise Exception(f"Could not find destination: {city_name}")
            
            # Get first destination ID
            dest_id = dest_data["data"][0]["dest_id"]
            search_type = dest_data["data"][0]["search_type"]
            
            # Step 2: Search hotels
            hotels_url = f"{self.base_url}/hotels/searchHotels"
            hotels_params = {
                "dest_id": dest_id,
                "search_type": search_type,
                "arrival_date": check_in,
                "departure_date": check_out,
                "adults": adults,
                "room_qty": rooms,
                "currency_code": currency,
                "units": "metric",
                "page_number": 1,
                "languagecode": "en-us"
            }
            
            hotels_response = requests.get(hotels_url, headers=self.headers, params=hotels_params, timeout=30)
            hotels_response.raise_for_status()
            return hotels_response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Booking.com hotels search failed: {str(e)}")


# Singleton instance
_booking_client = None

def get_booking_client() -> BookingAPIClient:
    """Get or create BookingAPIClient singleton"""
    global _booking_client
    if _booking_client is None:
        _booking_client = BookingAPIClient()
    return _booking_client


# ============================================
# Agent Tool Functions
# ============================================

def search_flights_booking(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    cabin_class: str = "ECONOMY",
    max_price: Optional[float] = None,
    max_stops: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for flights using Booking.com API and return structured flight cards.
    Supports city names or airport codes (automatically converts to Booking.com IDs).
    
    Args:
        origin: Origin city or airport (e.g., 'New York', 'JFK', 'Seoul')
        destination: Destination city or airport (e.g., 'Paris', 'CDG', 'Tokyo')
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date for round trip (optional)
        passengers: Number of passengers
        cabin_class: 'ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST'
        max_price: Maximum price in USD (optional)
        max_stops: Maximum stops - 'none' (direct), '1', '2+' (optional)
        
    Returns:
        Dictionary with flight cards in standardized format
    """
    try:
        client = get_booking_client()
        
        # Step 1: Get origin airport ID
        origin_data = client.search_flight_destination(origin)
        if not origin_data.get("data"):
            return {
                "type": "error_result",
                "cards": [{
                    "type": "confirmation",
                    "id": f"error_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "success": False,
                        "message": f"Could not find origin airport: {origin}",
                        "error_type": "invalid_location"
                    }
                }],
                "metadata": {"error": f"Origin not found: {origin}"}
            }
        
        from_id = origin_data["data"][0]["id"]
        origin_name = origin_data["data"][0]["name"]
        
        # Step 2: Get destination airport ID
        dest_data = client.search_flight_destination(destination)
        if not dest_data.get("data"):
            return {
                "type": "error_result",
                "cards": [{
                    "type": "confirmation",
                    "id": f"error_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "success": False,
                        "message": f"Could not find destination airport: {destination}",
                        "error_type": "invalid_location"
                    }
                }],
                "metadata": {"error": f"Destination not found: {destination}"}
            }
        
        to_id = dest_data["data"][0]["id"]
        dest_name = dest_data["data"][0]["name"]
        
        # Step 3: Search flights
        stops_filter = max_stops if max_stops else "none"
        
        flight_data = client.search_flights(
            from_id=from_id,
            to_id=to_id,
            depart_date=departure_date,
            return_date=return_date,
            adults=passengers,
            cabin_class=cabin_class.upper(),
            stops=stops_filter
        )
        
        # Parse response - Booking.com format
        if not flight_data.get("status"):
            return {
                "type": "flight_search_result",
                "cards": [],
                "metadata": {
                    "source": "Booking.com API",
                    "message": flight_data.get("message", "API request failed"),
                    "origin": origin_name,
                    "destination": dest_name
                }
            }
        
        data = flight_data.get("data", {})
        flight_offers = data.get("flightOffers", [])
        
        if not flight_offers:
            return {
                "type": "flight_search_result",
                "cards": [],
                "metadata": {
                    "source": "Booking.com API",
                    "message": f"No flights found from {origin_name} to {dest_name}",
                    "origin": origin_name,
                    "destination": dest_name
                }
            }
        
        # Convert to flight cards
        flight_cards = []
        for offer in flight_offers[:15]:  # Limit to 15
            # Get price from priceBreakdown
            price_breakdown = offer.get("priceBreakdown", {})
            total = price_breakdown.get("total", {})
            price_units = total.get("units", 0)
            price_nanos = total.get("nanos", 0)
            total_price = price_units + (price_nanos / 1_000_000_000)
            
            # Filter by price
            if max_price and total_price > max_price:
                continue
            
            # Get segments (each offer has multiple segments for multi-leg flights)
            segments = offer.get("segments", [])
            if not segments:
                continue
            
            first_segment = segments[0]
            last_segment = segments[-1]
            
            # Get airline info from first leg of first segment
            first_leg = first_segment.get("legs", [{}])[0]
            carriers_data = first_leg.get("carriersData", [])
            
            if carriers_data:
                airline_name = carriers_data[0].get("name", "Unknown Airline")
                airline_logo = carriers_data[0].get("logo", "")
            else:
                airline_name = "Unknown Airline"
                airline_logo = ""
            
            # Get flight numbers from all legs
            flight_numbers = []
            for segment in segments:
                for leg in segment.get("legs", []):
                    flight_info = leg.get("flightInfo", {})
                    carrier_info = flight_info.get("carrierInfo", {})
                    carrier_code = carrier_info.get("operatingCarrier", "")
                    flight_num = flight_info.get("flightNumber", "")
                    if carrier_code and flight_num:
                        flight_numbers.append(f"{carrier_code}{flight_num}")
            
            flight_number = ", ".join(flight_numbers) if flight_numbers else "N/A"
            
            # Get departure and arrival info
            departure_airport = first_segment.get("departureAirport", {})
            arrival_airport = last_segment.get("arrivalAirport", {})
            
            origin_code = departure_airport.get("code", origin)
            dest_code = arrival_airport.get("code", destination)
            
            departure_time = first_segment.get("departureTime", "")
            arrival_time = last_segment.get("arrivalTime", "")
            
            # Calculate total duration (sum of all segment times)
            total_time_seconds = sum(seg.get("totalTime", 0) for seg in segments)
            duration_hours = round(total_time_seconds / 3600, 1) if total_time_seconds else 0
            
            # Count stops (number of legs - 1 for each segment)
            total_stops = 0
            for segment in segments:
                legs = segment.get("legs", [])
                total_stops += max(0, len(legs) - 1)
            
            # Get cabin class
            cabin_class_actual = cabin_class
            if segments and segments[0].get("legs"):
                cabin_class_actual = segments[0]["legs"][0].get("cabinClass", cabin_class)
            
            flight_cards.append({
                "type": "flight",
                "id": f"flight_{uuid.uuid4().hex[:8]}",
                "data": {
                    "airline": airline_name,
                    "airline_logo": airline_logo,
                    "flight_number": flight_number,
                    "origin": origin_code,
                    "destination": dest_code,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "duration": duration_hours,
                    "price": round(total_price, 2),
                    "currency": total.get("currencyCode", "USD"),
                    "stops": total_stops,
                    "cabin_class": cabin_class_actual,
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "booking_token": offer.get("token", "")
                }
            })
        
        return {
            "type": "flight_search_result",
            "cards": flight_cards,
            "metadata": {
                "source": "Booking.com API",
                "query": f"{origin_name} → {dest_name}",
                "departure_date": departure_date,
                "return_date": return_date,
                "passengers": passengers,
                "cabin_class": cabin_class,
                "total_results": len(flight_cards)
            }
        }
    
    except Exception as e:
        # Return error as confirmation card
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Failed to search flights: {str(e)}",
                    "error_type": "api_error"
                }
            }],
            "metadata": {"error": str(e)}
        }


def search_hotels_booking(
    city: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    rooms: int = 1,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None
) -> Dict[str, Any]:
    """
    Search for hotels using Booking.com API and return structured hotel cards.
    
    Args:
        city: City name (e.g., 'Paris', 'New York', 'Seoul')
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests
        rooms: Number of rooms
        max_price: Maximum price per night in USD (optional)
        min_rating: Minimum rating 1-10 (optional)
        
    Returns:
        Dictionary with hotel cards in standardized format
    """
    try:
        client = get_booking_client()
        
        # Search hotels
        hotel_data = client.search_hotels_booking(
            city_name=city,
            check_in=check_in,
            check_out=check_out,
            adults=guests,
            rooms=rooms
        )
        
        # Parse response - Booking.com hotel format
        hotels = hotel_data.get("data", {}).get("hotels", [])
        
        if not hotels:
            return {
                "type": "hotel_search_result",
                "cards": [],
                "metadata": {
                    "source": "Booking.com API",
                    "message": f"No hotels found in {city}"
                }
            }
        
        # Calculate nights
        try:
            nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
        except:
            nights = 1
        
        # Convert to hotel cards
        hotel_cards = []
        for hotel_obj in hotels[:15]:  # Limit to 15
            # Get property data (actual hotel info is inside 'property' key)
            hotel = hotel_obj.get("property", {})
            if not hotel:
                continue
            
            # Get price
            price_breakdown = hotel.get("priceBreakdown", {})
            gross_price_obj = price_breakdown.get("grossPrice", {})
            gross_price = gross_price_obj.get("value", 0)
            currency = gross_price_obj.get("currency", hotel.get("currency", "USD"))
            
            price_per_night = gross_price / nights if nights > 0 else gross_price
            
            # Filter by price
            if max_price and price_per_night > max_price:
                continue
            
            # Get rating
            review_score = hotel.get("reviewScore", 0)
            rating = review_score / 2  # Convert 0-10 to 0-5
            
            # Filter by rating
            if min_rating and review_score < min_rating:
                continue
            
            # Get photo
            photo_urls = hotel.get("photoUrls", [])
            image_url = photo_urls[0] if photo_urls else None
            
            # Get location info
            latitude = hotel.get("latitude")
            longitude = hotel.get("longitude")
            
            # Get property class (star rating)
            property_class = hotel.get("propertyClass", 0)
            accurate_class = hotel.get("accuratePropertyClass", property_class)
            
            hotel_cards.append({
                "type": "hotel",
                "id": f"hotel_{uuid.uuid4().hex[:8]}",
                "data": {
                    "name": hotel.get("name", "Unknown Hotel"),
                    "price": round(price_per_night, 2),
                    "price_unit": "night",
                    "total_price": round(gross_price, 2),
                    "currency": currency,
                    "rating": round(rating, 1),
                    "review_score": review_score,
                    "review_score_word": hotel.get("reviewScoreWord", ""),
                    "review_count": hotel.get("reviewCount", 0),
                    "location": f"{latitude}, {longitude}" if latitude and longitude else "",
                    "image": image_url,
                    "check_in": check_in,
                    "check_out": check_out,
                    "nights": nights,
                    "hotel_id": hotel_obj.get("hotel_id", hotel.get("id")),
                    "stars": accurate_class,
                    "country_code": hotel.get("countryCode", ""),
                    "is_preferred": hotel.get("isPreferred", False)
                }
            })
        
        return {
            "type": "hotel_search_result",
            "cards": hotel_cards,
            "metadata": {
                "source": "Booking.com API",
                "query_location": city,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "rooms": rooms,
                "total_results": len(hotel_cards)
            }
        }
    
    except Exception as e:
        # Return error as confirmation card
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
# Helper Functions (reuse from amadeus_search.py)
# ============================================

def _get_airport_code(location: str) -> str:
    """Convert city/airport name to IATA airport code"""
    airport_codes = {
        # Asia
        "seoul": "ICN", "gimpo": "GMP",
        "tokyo": "NRT", "haneda": "HND",
        "osaka": "KIX", "itami": "ITM",
        "beijing": "PEK", "daxing": "PKX",
        "shanghai": "PVG", "hongqiao": "SHA",
        "hong kong": "HKG",
        "singapore": "SIN",
        "bangkok": "BKK",
        "taipei": "TPE",
        "kuala lumpur": "KUL",
        
        # Europe
        "london": "LHR", "gatwick": "LGW",
        "paris": "CDG", "orly": "ORY",
        "rome": "FCO",
        "barcelona": "BCN",
        "madrid": "MAD",
        "berlin": "BER",
        "amsterdam": "AMS",
        "vienna": "VIE",
        "prague": "PRG",
        "istanbul": "IST",
        
        # North America
        "new york": "JFK", "newark": "EWR", "laguardia": "LGA",
        "los angeles": "LAX",
        "san francisco": "SFO",
        "chicago": "ORD", "midway": "MDW",
        "miami": "MIA",
        "las vegas": "LAS",
        "toronto": "YYZ",
        "vancouver": "YVR",
        "mexico city": "MEX",
        
        # Oceania
        "sydney": "SYD",
        "melbourne": "MEL",
        "auckland": "AKL",
        
        # Middle East
        "dubai": "DXB",
        "abu dhabi": "AUH",
        
        # South America
        "sao paulo": "GRU",
        "rio de janeiro": "GIG",
        "buenos aires": "EZE",
    }
    
    normalized = location.lower().strip()
    
    if normalized in airport_codes:
        return airport_codes[normalized]
    
    for loc, code in airport_codes.items():
        if normalized in loc or loc in normalized:
            return airport_codes[loc]
    
    return location[:3].upper()
