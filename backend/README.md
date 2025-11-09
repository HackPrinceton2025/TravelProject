# TravelSmith Backend

An intelligent AI-powered travel planning assistant built with FastAPI, featuring conversational group trip planning, real-time collaboration, and integration with multiple travel APIs.

## Features

- 🤖 **AI Travel Agent**: Conversational agent powered by Claude/Grok via Dedalus SDK
- 🔍 **Multi-API Integration**: Google Maps, Booking.com, Foursquare, Ticketmaster
- 👥 **Group Collaboration**: Shared preferences, polls, and expense tracking
- ⚡ **Real-time Updates**: Supabase-powered live synchronization
- 🚀 **High Performance**: Parallel API processing with ThreadPoolExecutor
- 📊 **Structured Responses**: Pydantic schemas for type-safe data validation

## Setup

### Prerequisites

- Python 3.8+
- Supabase account and project
- API keys for:
  - Google Maps API (Places, Directions, Geocoding)
  - RapidAPI (Booking.com integration)
  - Anthropic Claude or Grok API

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (create `.env` file):
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
RAPIDAPI_KEY=your_rapidapi_key
ANTHROPIC_API_KEY=your_anthropic_key
```

3. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Routes

### Core Endpoints

- **`/api/groups`** - Group management (create, read, update, delete)
- **`/api/users`** - User authentication and profile management
- **`/api/group_members`** - Group membership operations
- **`/api/messages`** - Conversation history and messaging
- **`/api/agent`** - AI agent interactions and tool calling
- **`/api/polls`** - Group decision-making polls
- **`/api/preferences`** - Individual and group travel preferences
- **`/api/expenses`** - Expense tracking and budget management

### Agent Tools

The AI agent has access to multiple specialized tools:

- **Google Maps Tools**: Restaurant search, attraction discovery, hotel lookup, transportation routes
- **Booking.com Tools**: Flight search, hotel availability with real-time pricing
- **Budget Tools**: Expense tracking, budget recommendations
- **Poll Tools**: Create and manage group voting
- **Preference Tools**: Aggregate and manage travel preferences
- **Location Tools**: Geocoding and location context

### MCP Server Integration

- **Brave Search**: Web search for travel information
- **Ticketmaster**: Event and activity discovery
- **Sonar**: Enhanced search capabilities

## Architecture

```
backend/
├── agent/              # AI agent core logic
│   ├── dedalus_client.py
│   ├── runner.py
│   ├── prompts/        # Domain-specific prompts
│   └── tools/          # Agent tool implementations
├── routes/             # FastAPI route handlers
├── models/             # Pydantic schemas and DB models
├── core/               # Configuration and database
├── utils/              # Helper utilities
└── test/               # Test suite
```

## Key Features

### Parallel API Processing

Optimized performance with ThreadPoolExecutor for concurrent API calls:
- **Before**: 15 seconds for 7 location searches
- **After**: 2 seconds for 7 location searches
- 7-8x performance improvement

### Domain-Specific Prompts

Specialized prompts for different travel planning aspects:
- Hotels, restaurants, attractions
- Flights and transportation
- Budgets and expenses
- Group preferences and polls

### Real-time Collaboration

Supabase integration enables:
- Live message synchronization
- Real-time poll updates
- Instant preference changes
- Collaborative expense tracking

## Development

### Running Tests

```bash
# Run specific test file
python -m pytest test/test_agent.py

# Run all tests
python -m pytest test/
```

### Code Structure

- **Models** (`models/schemas.py`): Pydantic models for API responses
- **Routes** (`routes/`): FastAPI endpoint implementations
- **Agent Tools** (`agent/tools/`): Individual tool function implementations
- **Prompts** (`agent/prompts/`): AI agent system and domain prompts

## Technology Stack

- **Framework**: FastAPI
- **AI Orchestration**: Dedalus SDK
- **LLM**: Claude (Anthropic) / Grok
- **Database**: Supabase (PostgreSQL)
- **APIs**: Google Maps, RapidAPI, Foursquare
- **Validation**: Pydantic v2
- **Concurrency**: Python concurrent.futures

## Performance Optimizations

- Parallel API calls with ThreadPoolExecutor (max_workers=10)
- Result limiting (max 7 items per search)
- Efficient error handling with detailed logging
- Type-safe responses for frontend integration

## Contributing

1. Follow the existing code structure
2. Add type hints to all functions
3. Update relevant domain prompts when modifying tools
4. Test agent responses with `test/test_agent.py`
5. Ensure Pydantic schemas match actual responses

## License

[Add your license here]


