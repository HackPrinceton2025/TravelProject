from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routes
from routes import expenses

app = FastAPI(
    title="TravelApp Expense Splitter API",
    version="1.0.0",
    description="Backend API for group expense tracking and bill splitting."
)

# --- CORS (allow frontend and testing tools to connect) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])

# --- Health check ---
@app.get("/")
def root():
    return {"message": "Expense Splitter backend running 🚀"}
