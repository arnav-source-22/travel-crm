from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Travel CRM AI", version="1.0")

# ── Request models ─────────────────────────────────────────────
class BookingRequest(BaseModel):
    customer_name: str
    details: str

class ItineraryRequest(BaseModel):
    destination: str
    days: int
    interests: str
    budget: int

class LeadRequest(BaseModel):
    name: str
    destinations: str
    message_count: int
    days_since_contact: int
    budget: Optional[str] = "Not specified"
    travel_month: Optional[str] = "Unknown"
    email_responded: Optional[bool] = False

class EmailRequest(BaseModel):
    name: str
    destination: str

# ── Endpoints ──────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Travel CRM AI is running!"}

@app.post("/booking/create")
def create_booking(req: BookingRequest):
    return {
        "status": "confirmed",
        "customer": req.customer_name,
        "details": req.details,
        "message": "Booking created successfully"
    }

@app.post("/booking/itinerary")
def get_itinerary(req: ItineraryRequest):
    return {
        "destination": req.destination,
        "days": req.days,
        "interests": req.interests,
        "budget": req.budget,
        "message": "Itinerary generated successfully"
    }

@app.post("/lead/score")
def score_lead(req: LeadRequest):
    # Simple scoring logic
    score = 0
    if req.message_count >= 8: score += 30
    elif req.message_count >= 4: score += 15
    if req.days_since_contact <= 2: score += 30
    elif req.days_since_contact <= 7: score += 15
    if req.email_responded: score += 20
    if req.budget != "Not specified": score += 20

    category = "HOT" if score >= 75 else "WARM" if score >= 45 else "COLD"
    return {
        "name": req.name,
        "score": score,
        "category": category,
        "action": "Call within 24 hours" if category == "HOT" else "Follow up in 3 days" if category == "WARM" else "Add to newsletter"
    }

@app.post("/lead/email")
def draft_email(req: EmailRequest):
    return {
        "subject": f"Your {req.destination} holiday — exclusive offer inside",
        "email": f"Hi {req.name},\n\nThank you for your interest in {req.destination}! We have curated exclusive packages just for you.\n\nWarm regards,\nTravel CRM Team"
    }