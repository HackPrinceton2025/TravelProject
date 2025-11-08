from backend.routes import polls
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routes
from routes import groups, messages, polls, agent, expenses, users, group_members

app = FastAPI(
    title="TravelApp Expense Splitter API",
    version="1.0.0",
    description="Backend API for group expense tracking and bill splitting."
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(group_members.router, prefix="/api/group_members", tags=["group_members"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(polls.router, prefix="/api/polls", tags=["polls"])
app.include_router(polls.router, prefix="/api", tags=["polls-v2"])

# --- Health check ---
@app.get("/")
def root():
    return {"message": "Expense Splitter backend running successfully"}
