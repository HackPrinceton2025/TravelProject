from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import users, groups, group_members, messages, agent ## will add more routes here



app = FastAPI(title="TravelProject API")

# Allow local frontend by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(group_members.router, prefix="/api/group_members", tags=["group_members"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])



@app.get("/")
def root():
    return {"status": "TravelProject API running"}


