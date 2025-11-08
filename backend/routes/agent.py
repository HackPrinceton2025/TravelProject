## this is a placeholder for the agent routes
## @TODO: implement the agent routes
## Aaron will work here

from fastapi import APIRouter

router = APIRouter()

@router.post("/plan-trip")
def plan_trip(payload: dict):
    # later this will call Dedalus or Claude APIs
    return {"message": "AI planning endpoint placeholder"}
