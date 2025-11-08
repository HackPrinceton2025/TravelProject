from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import messages, groups, agent ## will add more routes here



app = FastAPI(title="TravelProject API")

# Allow local frontend by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])



@app.get("/")
def root():
    return {"status": "TravelProject API running"}


