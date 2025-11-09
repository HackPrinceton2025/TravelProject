# TravelSmith: AI Group Travel Planning Platform

TravelSmith is an AI-powered group travel planning platform where multiple users collaborate through real-time chat with an intelligent agent that learns individual preferences and searches across travel APIs to provide personalized recommendations. The AI maintains conversation context, suggests options satisfying the group's collective constraints, and facilitates decision-making through integrated polling and expense tracking.

## 🚀 Project Goal

Build a real-time collaborative travel planning application where an AI agent assists groups in organizing trips by providing context-aware recommendations based on individual preferences, live chat conversations, and historical context.

## ✨ Features

### 🤖 AI Travel Agent
- **Conversational Interface**: Natural language interaction with @ai_agent mentions
- **Context-Aware Intelligence**: Recommendations based on user preferences, recent chat, and conversation history
- **Multi-API Integration**: Google Maps, Booking.com, Foursquare, Ticketmaster
- **Tool-Based Search**: Executes real searches for flights, hotels, restaurants, and activities
- **Powered by**: Gpt via Dedalus SDK

### 👥 Group Collaboration
- **Real-time Chat**: Live group conversations with Supabase synchronization
- **Preference Onboarding**: Individual travel profiles (budget, dates, interests, dietary restrictions)s
- **Expense Tracking**: Shared cost management and budget recommendations

### 🔧 Smart Travel Tools
- **Flight Search**: Real-time availability and pricing via Kiwi.com API
- **Hotel Discovery**: Location-based search with Google Maps integration
- **Restaurant Recommendations**: Dietary-aware suggestions
- **Activity Planning**: Event discovery via Ticketmaster
- **Budget Management**: Expense tracking and recommendations

### ⚡ Performance
- **Parallel API Processing**: 7-8x speedup with ThreadPoolExecutor
- **Type-Safe APIs**: Pydantic schemas for validation
- **Real-time Updates**: Live synchronization across all group members

## 🏗️ Project Structure

```
TravelProject/
├── backend/                    # FastAPI Backend
│   ├── agent/                  # AI Agent Core
│   │   ├── dedalus_client.py   # Dedalus SDK wrapper
│   │   ├── runner.py           # Agent orchestration
│   │   ├── prompts/            # Domain-specific prompts
│   │   │   ├── system_claude.txt
│   │   │   ├── domain_flights.txt
│   │   │   ├── domain_hotels.txt
│   │   │   ├── domain_restaurants.txt
│   │   │   └── examples.json
│   │   └── tools/              # Agent tool implementations
│   │       ├── google_maps.py  # Places, directions, geocoding
│   │       ├── kiwi_flights.py # Flight search
│   │       ├── rapidapi_search.py # Hotel search
│   │       ├── preferences.py  # User preference management
│   │       └── polls.py        # Voting system
│   ├── routes/                 # API Endpoints
│   │   ├── agent.py            # AI chat endpoint
│   │   ├── groups.py           # Group management
│   │   ├── messages.py         # Chat messages
│   │   ├── preferences.py      # Preference CRUD
│   │   ├── polls.py            # Poll operations
│   │   └── expenses.py         # Expense tracking
│   ├── models/                 # Data Models
│   │   ├── schemas.py          # Pydantic schemas
│   │   └── db_models.py        # Database models
│   ├── core/                   # Configuration
│   │   ├── config.py           # Environment settings
│   │   └── database.py         # Supabase client
│   ├── utils/                  # Utilities
│   │   ├── supabase_client.py
│   │   └── message_utils.py
│   ├── test/                   # Test Suite
│   └── main.py                 # FastAPI app entry point
│
└── frontend/                   # Next.js Frontend (in progress)
    ├── app/
    │   ├── components/         # React components
    │   ├── lib/                # Frontend utilities
    │   └── page.tsx            # Main page
    └── ...
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Node.js 18+** (for frontend)
- **Supabase account and project**
- **API Keys**:
  - Dedalus API key (for Claude/Grok)
  - Google Maps API key
  - RapidAPI key (Booking.com)
  - Kiwi.com API key (optional)

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment** (create `.env` file):
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# AI Agent
DEDALUS_API_BASE=https://api.dedalus.ai
DEDALUS_API_KEY=your_dedalus_key

# Travel APIs
GOOGLE_MAPS_API_KEY=your_google_maps_key
RAPIDAPI_KEY=your_rapidapi_key
KIWI_API_KEY=your_kiwi_key
```

4. **Run the server**:
```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

### Frontend Setup *(in progress)*

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment** (create `.env.local`):
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Run development server**:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📡 API Documentation

### Core Endpoints

**Group Management**
- `POST /api/groups` - Create new group
- `GET /api/groups/{group_id}` - Get group details
- `GET /api/groups` - List all groups
- `DELETE /api/groups/{group_id}` - Delete group

**User & Preferences**
- `POST /api/preferences` - Save user preferences
- `GET /api/preferences/{group_id}` - Get all group preferences
- `GET /api/preferences/{group_id}/{user_id}` - Get user preferences

**Chat & AI Agent**
- `POST /api/messages` - Send message to group
- `GET /api/messages/{group_id}` - Get chat history
- `POST /api/agent/chat` - Interact with AI agent

**Collaboration Tools**
- `POST /api/polls` - Create poll
- `POST /api/polls/{poll_id}/vote` - Vote on option
- `GET /api/polls/{group_id}` - Get group polls
- `POST /api/expenses` - Track expense
- `GET /api/expenses/{group_id}` - Get group expenses

### AI Agent Tools

The agent has access to 10+ specialized tools:

1. **`search_flights`** - Find flights matching budget and dates
2. **`find_stays`** - Search hotels near destination
3. **`search_restaurants`** - Get dining recommendations with dietary filters
4. **`find_attractions`** - Discover activities and tourist spots
5. **`find_events`** - Search concerts, sports, theater via Ticketmaster
6. **`get_directions`** - Calculate routes and travel time
7. **`get_user_preferences`** - Access individual travel preferences
8. **`get_group_preferences`** - Analyze group consensus
9. **`create_poll`** - Generate decision polls

## 🧠 AI Context System

### User Preferences (Long-term Memory)
Stored in Supabase database:
- Budget constraints and spending limits
- Available travel dates (start/end)
- Interests (museums, nightlife, nature, etc.)
- Dietary restrictions (vegetarian, gluten-free, allergies)
- Preferred travel pace (fast-paced, moderate, relaxed)
- Departure city and destination preferences

### Real-time Collaboration

Supabase integration enables:
- **Live message synchronization**: See messages instantly across all devices
- **Instant preference changes**: Updates reflect immediately for the AI
- **Collaborative expense tracking**: Shared visibility of all group spending

## 🧪 Testing

```bash
# Navigate to backend
cd backend

# Run all tests
python -m pytest test/

# Test specific components
python -m pytest test/test_agent.py          # AI agent functionality
python -m pytest test/test_preferences.py    # Preference system
python -m pytest test/test_google_maps.py    # Google Maps integration
python -m pytest test/test_kiwi_flights.py   # Flight search
python -m pytest test/test_polls.py          # Voting system
```

## 💻 Technology Stack

### Backend
- **Framework**: FastAPI
- **AI Orchestration**: Dedalus SDK
- **LLM**: Openai GPT 4.1
- **Database**: Supabase (PostgreSQL with real-time subscriptions)
- **APIs**: Google Maps, RapidAPI, Ticketmaster, Booking.com
- **Validation**: Pydantic v2
- **Concurrency**: Python concurrent.futures (ThreadPoolExecutor)

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Real-time**: Supabase subscriptions

## 🙏 Acknowledgments

- **Dedalus SDK** for AI orchestration and tool calling
- **OpenAI** for natural language understanding
- **Supabase** for real-time database and authentication
- **Google Maps API** for location services
- **RapidAPI** for travel data aggregation
- **HackPrinceton 2025** for the opportunity to build this project
