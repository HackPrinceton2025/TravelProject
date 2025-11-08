from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import groups, messages, polls, agent

app = FastAPI(title="TravelProject API")

# Allow local frontend by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groups.router, prefix="/api/groups")
app.include_router(messages.router, prefix="/api/messages")
app.include_router(polls.router, prefix="/api/polls")
app.include_router(agent.router, prefix="/api/agent")


@app.get("/")
def root():
    return {"status": "TravelProject API running"}


