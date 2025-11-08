# Travel Agent Tools Analysis
# Last Updated: 2025-11-08

## ✅ Already Implemented via MCP Servers

1. **foursquare-places-mcp** - Search for places and place recommendations
   - Restaurants, cafes, bars
   - Tourist attractions
   - Shopping locations
   - Local businesses

2. **brave-search-mcp** - Web search and local search
   - General web searches
   - Local business information
   - Current events and news

3. **ticketmaster-mcp** - Events and attractions
   - Concerts, sports events
   - Theater shows
   - Event tickets and venues

4. **sonar (Perplexity)** - Advanced web searches
   - Real-time information
   - Complex queries with reasoning

5. **general-mcp** - Time and date utilities
   - Current time/date
   - Timezone conversions
   - Date calculations


## 🔨 Tools to Implement (Custom)

### 1. User Location & Preferences
- **get_user_location** (PRIORITY)
  - Get user's current location (city, country, coordinates)
  - Input: user_id
  - Output: location data with coordinates
  - Use case: "Find restaurants near me"

- **get_user_preferences**
  - Fetch stored user travel preferences
  - Input: user_id
  - Output: budget, interests, dietary restrictions, etc.
  - Use case: Personalized recommendations

- **update_user_preferences**
  - Update user's travel preferences
  - Input: user_id, preferences dict
  - Output: confirmation
  - Use case: Onboarding, preference changes


### 2. Group Management
- **get_group_members**
  - Get all members in a travel group
  - Input: group_id
  - Output: list of users with their preferences
  - Use case: "Show me everyone's budget constraints"

- **get_group_consensus**
  - Analyze group preferences to find common ground
  - Input: group_id, preference_type (budget, dates, interests)
  - Output: consensus data, conflicts, recommendations
  - Use case: "What dates work for everyone?"

- **create_poll**
  - Create a voting poll for the group
  - Input: group_id, question, options
  - Output: poll_id
  - Use case: "Let's vote on which hotel to book"

- **get_poll_results**
  - Get current results of a poll
  - Input: poll_id
  - Output: vote counts, winner
  - Use case: Check voting status


### 3. Budget & Expense Management
- **calculate_budget** ✅ (Already implemented, but needs enhancement)
  - Current: Basic allocation
  - Enhancement needed: Group member splitting, currency conversion

- **track_expense** ✅ (Already implemented, needs DB integration)
  - Current: Basic tracking
  - Enhancement needed: Save to database, OCR receipt scanning

- **get_group_expenses**
  - Get all expenses for a trip
  - Input: group_id
  - Output: list of expenses with who paid
  - Use case: "Show me our expenses so far"

- **calculate_expense_split**
  - Calculate how much each person owes
  - Input: group_id, expenses list
  - Output: settlement amounts (who owes whom)
  - Use case: "Split the bill fairly"

- **convert_currency**
  - Convert between currencies
  - Input: amount, from_currency, to_currency
  - Output: converted amount with exchange rate
  - Use case: International travel budgeting


### 4. Trip Planning & Itinerary
- **generate_itinerary** ✅ (Already implemented, needs enhancement)
  - Current: Basic placeholder
  - Enhancement needed: Use MCP servers for real recommendations

- **save_itinerary**
  - Save itinerary to database
  - Input: group_id, itinerary data
  - Output: itinerary_id
  - Use case: Persist planned itinerary

- **get_saved_itineraries**
  - Get saved itineraries for a group
  - Input: group_id
  - Output: list of itineraries
  - Use case: "Show me our saved plans"

- **optimize_itinerary**
  - Optimize route/timing for saved itinerary
  - Input: itinerary data, optimization_criteria (time/cost/distance)
  - Output: optimized itinerary
  - Use case: "Find the most efficient route"


### 5. Transportation
- **search_flights** ✅ (Already implemented, needs real API)
  - Current: Mock data
  - Enhancement needed: Integrate with Amadeus/Skyscanner API

- **compare_transportation**
  - Compare different transport options (flight, train, bus, car)
  - Input: origin, destination, date
  - Output: comparison cards with prices, duration
  - Use case: "Should we fly or take the train?"

- **get_directions** ✅ (Already implemented, needs Google Maps API)
  - Current: Mock data
  - Enhancement needed: Integrate with Google Maps API


### 6. Accommodation
- **find_stays** ✅ (Already implemented, needs real API)
  - Current: Mock data
  - Enhancement needed: Integrate with Booking.com/Airbnb API

- **compare_accommodations**
  - Compare different accommodation options
  - Input: location, dates, budget
  - Output: comparison table with pros/cons
  - Use case: "Compare hotels vs Airbnb"


### 7. Booking & Reservations (Future)
- **create_booking_link**
  - Generate booking links for hotels/flights
  - Input: item details
  - Output: affiliate booking link
  - Use case: Easy booking from chat

- **check_availability**
  - Check real-time availability
  - Input: hotel/flight details
  - Output: availability status
  - Use case: "Is this hotel still available?"


### 8. Context & Memory
- **save_chat_context**
  - Save important decisions from chat
  - Input: group_id, context_type, data
  - Output: confirmation
  - Use case: Remember decisions made in chat

- **get_trip_summary**
  - Get summary of all trip planning so far
  - Input: group_id
  - Output: comprehensive summary
  - Use case: "Summarize our plans so far"

- **search_chat_history**
  - Search through past conversations
  - Input: group_id, query
  - Output: relevant messages
  - Use case: "What did we decide about hotels?"


## 🎯 Priority Order

### Phase 1 (MVP - Essential)
1. get_user_location ⭐⭐⭐
2. get_group_members ⭐⭐⭐
3. get_group_expenses ⭐⭐⭐
4. calculate_expense_split ⭐⭐⭐
5. create_poll ⭐⭐⭐
6. get_poll_results ⭐⭐⭐

### Phase 2 (Enhanced Experience)
7. get_user_preferences ⭐⭐
8. update_user_preferences ⭐⭐
9. get_group_consensus ⭐⭐
10. save_itinerary ⭐⭐
11. get_saved_itineraries ⭐⭐
12. convert_currency ⭐⭐

### Phase 3 (Real API Integration)
13. Integrate real flight API (Amadeus/Skyscanner)
14. Integrate real hotel API (Booking.com)
15. Integrate Google Maps for directions
16. OCR for receipt scanning

### Phase 4 (Advanced Features)
17. optimize_itinerary
18. compare_transportation
19. compare_accommodations
20. save_chat_context
21. get_trip_summary
22. search_chat_history


## 📝 Notes

- Tools marked with ✅ are already scaffolded but need enhancement
- MCP servers provide: places, web search, events, weather, time/date
- Focus on group collaboration features (polls, expense splitting, consensus)
- All tools should return card-formatted data for consistent UI rendering
- Database integration needed for persistence (Supabase already set up)