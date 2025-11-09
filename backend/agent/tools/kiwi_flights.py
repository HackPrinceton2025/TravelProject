import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests  # type: ignore[import]

RAPIDAPI_HOST = "kiwi-com-cheap-flights.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}"


# =====================================================================================
# Helpers
# =====================================================================================

def _get_rapidapi_headers() -> Dict[str, str]:
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        raise ValueError("RAPIDAPI_KEY is not set. Please add it to your environment.")
    return {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }


def _format_location(value: str, default_prefix: str = "City") -> str:
    """Convert a user-friendly location string to Kiwi format.

    Kiwi accepts values like "City:london_gb" or "Airport:JFK". If the caller already supplies
    a formatted value (contains ':'), we simply return it. Otherwise we try to infer the type.
    """
    if not value:
        raise ValueError("Location value cannot be empty")

    value = value.strip()
    if ":" in value:
        # Already in Kiwi format (City:, Airport:, Country:, etc.)
        return value

    # If a 3-letter code is provided assume an airport code
    if len(value) == 3 and value.isalpha():
        return f"Airport:{value.upper()}"

    # Fallback: assume city name. Convert spaces to underscores and lowercase.
    slug = value.lower().replace(" ", "_")
    return f"{default_prefix}:{slug}"


def _to_bool_str(value: bool) -> str:
    return "true" if value else "false"


def _iso_or_none(dt: Optional[str]) -> Optional[str]:
    if not dt:
        return None
    try:
        # Ensure valid ISO format; accept YYYY-MM-DD only
        parsed = datetime.fromisoformat(dt)
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {dt}. Expected YYYY-MM-DD.")


def _extract_segment(segment: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a single flight segment into a compact structure."""
    source = segment.get("source", {})
    destination = segment.get("destination", {})
    carrier = segment.get("carrier", {})
    operating = segment.get("operatingCarrier", {})

    def _extract_station(station: Dict[str, Any]) -> Dict[str, Any]:
        city = station.get("city", {})
        country = station.get("country", {})
        return {
            "code": station.get("code"),
            "name": station.get("name"),
            "type": station.get("type"),
            "city": {
                "name": city.get("name"),
                "id": city.get("id"),
            },
            "country": {
                "code": country.get("code"),
                "id": country.get("id"),
            },
        }

    return {
        "departure_time_local": source.get("localTime"),
        "departure_time_utc": source.get("utcTime"),
        "arrival_time_local": destination.get("localTime"),
        "arrival_time_utc": destination.get("utcTime"),
        "departure_airport": _extract_station(source.get("station", {})),
        "arrival_airport": _extract_station(destination.get("station", {})),
        "duration_seconds": segment.get("duration"),
        "flight_number": segment.get("code"),
        "carrier": {
            "name": carrier.get("name"),
            "code": carrier.get("code"),
        },
        "operating_carrier": {
            "name": operating.get("name"),
            "code": operating.get("code"),
        },
        "cabin_class": segment.get("cabinClass"),
    }


def _parse_itinerary(itinerary: Dict[str, Any], currency: str) -> Optional[Dict[str, Any]]:
    try:
        price_info = itinerary.get("price", {})
        price_amount = float(price_info.get("amount"))
        display_currency = price_info.get("currency") or currency

        # Outbound / inbound segments
        outbound = itinerary.get("outbound") or itinerary.get("sector")
        inbound = itinerary.get("inbound")

        def _collect_segments(leg: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
            if not leg:
                return []
            segments = []
            for sector in leg.get("sectorSegments", []):
                segment = sector.get("segment")
                if segment:
                    segments.append(_extract_segment(segment))
            return segments

        outbound_segments = _collect_segments(outbound)
        inbound_segments = _collect_segments(inbound)

        # Determine summary fields using first/last segments
        def _first_segment(segments: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
            return segments[0] if segments else None

        def _last_segment(segments: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
            return segments[-1] if segments else None

        first_seg = _first_segment(outbound_segments)
        last_seg = _last_segment(outbound_segments)

        if not first_seg or not last_seg:
            return None

        outbound_departure = first_seg["departure_time_local"]
        outbound_arrival = last_seg["arrival_time_local"]

        main_carrier = first_seg["carrier"]["name"] or first_seg["operating_carrier"].get("name")
        main_carrier_code = first_seg["carrier"]["code"] or first_seg["operating_carrier"].get("code")
        flight_number = first_seg.get("flight_number")

        origin_airport = first_seg["departure_airport"].get("code")
        destination_airport = last_seg["arrival_airport"].get("code")

        total_segments = len(outbound_segments)
        total_stops = max(0, total_segments - 1)

        booking_edges = itinerary.get("bookingOptions", {}).get("edges", [])
        booking_link = None
        if booking_edges:
            url = booking_edges[0].get("node", {}).get("bookingUrl")
            if url:
                booking_link = f"https://www.kiwi.com{url}"

        return {
            "type": "flight",
            "id": f"flight_{uuid.uuid4().hex[:8]}",
            "data": {
                "airline": main_carrier,
                "airline_code": main_carrier_code,
                "flight_number": flight_number,
                "origin": origin_airport,
                "destination": destination_airport,
                "departure_time": outbound_departure,
                "arrival_time": outbound_arrival,
                "price": round(price_amount, 2),
                "currency": display_currency.upper(),
                "stops": total_stops,
                "cabin_class": first_seg.get("cabin_class"),
                "booking_link": booking_link,
                "legs": {
                    "outbound": outbound_segments,
                    "inbound": inbound_segments,
                },
            }
        }
    except Exception:
        return None


# =====================================================================================
# Public tool
# =====================================================================================

def search_flights_kiwi(
    origin: str,
    destination: str,
    departure_date: Optional[str] = None,
    return_date: Optional[str] = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    currency: str = "USD",
    cabin_class: str = "ECONOMY",
    max_price: Optional[float] = None,
    sort_by: str = "PRICE",
    sort_order: str = "ASCENDING",
    limit: int = 10,
    include_handbags: bool = True,
    include_checked_bags: bool = False,
) -> Dict[str, Any]:
    """
    Search for flights using the Kiwi.com Cheap Flights API on RapidAPI.

    This tool mirrors the restaurant-search behaviour: the agent can call it when the user asks
    for flights. Provide origin/destination (city or airport), optional travel dates, passengers,
    and a budget. The function returns flight cards consumable by the UI carousel.

    Args:
        origin: City or airport ("New York", "JFK", "City:london_gb", ...)
        destination: City or airport
        departure_date: YYYY-MM-DD (optional, if omitted Kiwi searches upcoming dates)
        return_date: YYYY-MM-DD (optional, if omitted a one-way search is performed)
        adults: Number of adult travellers
        children: Number of children travellers
        infants: Number of infants travellers
        currency: Currency code for prices (e.g., "USD")
        cabin_class: ECONOMY, BUSINESS, FIRST, etc.
        max_price: Optional price ceiling (filters out results above budget)
        sort_by: Kiwi sort strategy (PRICE, QUALITY, DURATION, etc.)
        sort_order: ASCENDING or DESCENDING
        limit: Maximum number of itineraries to return
        include_handbags: Whether to request cabin baggage in the search (affects price)
        include_checked_bags: Whether to request checked baggage in the search
    """

    try:
        headers = _get_rapidapi_headers()

        formatted_origin = _format_location(origin)
        formatted_destination = _format_location(destination)

        parsed_departure = _iso_or_none(departure_date)
        parsed_return = _iso_or_none(return_date)

        is_round_trip = parsed_return is not None
        endpoint = "/round-trip" if is_round_trip else "/one-way"

        params: Dict[str, Any] = {
            "source": formatted_origin,
            "destination": formatted_destination,
            "currency": currency.lower(),
            "locale": "en",
            "adults": str(adults),
            "children": str(children),
            "infants": str(infants),
            "handbags": "1" if include_handbags else "0",
            "holdbags": "1" if include_checked_bags else "0",
            "cabinClass": cabin_class.upper(),
            "sortBy": sort_by.upper(),
            "sortOrder": sort_order.upper(),
            "limit": str(limit),
            "applyMixedClasses": _to_bool_str(True),
            "allowReturnFromDifferentCity": _to_bool_str(True),
            "allowChangeInboundDestination": _to_bool_str(True),
            "allowChangeInboundSource": _to_bool_str(True),
            "allowDifferentStationConnection": _to_bool_str(True),
            "enableSelfTransfer": _to_bool_str(True),
            "allowOvernightStopover": _to_bool_str(True),
            "enableTrueHiddenCity": _to_bool_str(False),
            "enableThrowAwayTicketing": _to_bool_str(False),
            "transportTypes": "FLIGHT",
            "contentProviders": "KIWI",
        }

        if parsed_departure:
            params["outboundDate"] = parsed_departure
        if parsed_return:
            params["returnDate"] = parsed_return

        response = requests.get(
            f"{RAPIDAPI_BASE_URL}{endpoint}",
            headers=headers,
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        raw = response.json()

        itineraries = raw.get("itineraries", [])
        cards: List[Dict[str, Any]] = []
        for itinerary in itineraries:
            card = _parse_itinerary(itinerary, currency)
            if not card:
                continue
            price_value = card["data"]["price"]
            if max_price is not None and price_value > max_price:
                continue
            cards.append(card)

        return {
            "type": "flight_search_result",
            "cards": cards,
            "metadata": {
                "source": "Kiwi.com Cheap Flights API",
                "origin": formatted_origin,
                "destination": formatted_destination,
                "departure_date": parsed_departure,
                "return_date": parsed_return,
                "currency": currency.upper(),
                "total_results": len(cards),
                "raw_itineraries_count": len(itineraries),
            }
        }

    except requests.HTTPError as http_err:
        status = getattr(http_err.response, "status_code", "unknown")
        detail = getattr(http_err.response, "text", str(http_err))
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": f"Kiwi API request failed with status {status}",
                    "details": detail[:500],
                    "error_type": "api_error",
                }
            }],
            "metadata": {
                "error": str(http_err),
                "status_code": status,
            }
        }
    except Exception as exc:
        return {
            "type": "error_result",
            "cards": [{
                "type": "confirmation",
                "id": f"error_{uuid.uuid4().hex[:8]}",
                "data": {
                    "success": False,
                    "message": "Failed to search flights",
                    "details": str(exc),
                    "error_type": "internal_error",
                }
            }],
            "metadata": {
                "error": str(exc),
            }
        }
