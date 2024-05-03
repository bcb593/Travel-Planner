from pydantic import BaseModel

class ItineraryRequest(BaseModel):
    days: int
    city: str

class ItineraryResponse(BaseModel):
    itinerary: str
