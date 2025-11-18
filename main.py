import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Law Firm API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceRequest(BaseModel):
    message: str
    context: Optional[List[str]] = None

class VoiceResponse(BaseModel):
    reply: str
    intent: str
    suggestions: List[str]

HELP_TEXT = (
    "I'm your AI legal assistant. I can: book a consultation, share our practice areas, "
    "explain attorney bios, provide office hours and location, and help with contact details."
)

PRACTICE_AREAS = {
    "corporate": "Corporate and Commercial Law — entity formation, contracts, M&A, governance.",
    "litigation": "Civil and Commercial Litigation — disputes, arbitration, and mediation.",
    "ip": "Intellectual Property — trademarks, copyrights, licensing, brand protection.",
    "employment": "Employment Law — policies, compliance, investigations, disputes.",
    "real estate": "Real Estate — transactions, leases, development, and financing."
}

@app.get("/")
def read_root():
    return {"message": "Law Firm Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.post("/api/voice-intent", response_model=VoiceResponse)
def voice_intent(req: VoiceRequest):
    text = (req.message or "").strip().lower()

    # Simple rule-based NLU for demo
    intent = "small_talk"
    reply = ""
    suggestions: List[str] = []

    def areas_list() -> str:
        return ", ".join([k.title() for k in PRACTICE_AREAS.keys()])

    if any(k in text for k in ["book", "consult", "appointment", "schedule"]):
        intent = "book_consultation"
        reply = (
            "I can help you schedule a consultation. Would you like a 15-minute call or a 30-minute meeting? "
            "You can also use the contact form below and we’ll confirm by email."
        )
        suggestions = ["15-minute call", "30-minute meeting", "Contact form"]
    elif any(k in text for k in ["practice", "services", "areas", "specialize", "what do you do"]):
        intent = "practice_areas"
        reply = (
            f"We focus on {areas_list()}. Ask about any area for more details, for example: 'Tell me about Corporate'."
        )
        suggestions = [a.title() for a in PRACTICE_AREAS.keys()]
    elif any(k in text for k in ["corporate", "litigation", "ip", "intellectual", "employment", "real estate"]):
        intent = "area_detail"
        # find matching key
        area_key = None
        for key in PRACTICE_AREAS.keys():
            if key in text or (key == "ip" and ("ip" in text or "intellectual" in text)):
                area_key = key
                break
        if area_key:
            reply = PRACTICE_AREAS[area_key]
        else:
            reply = "We cover several areas. Which practice are you interested in?"
        suggestions = ["Book a consultation", "View attorneys"]
    elif any(k in text for k in ["attorney", "lawyer", "team", "who"]):
        intent = "attorneys"
        reply = (
            "Our attorneys combine top-tier expertise with practical business insight. "
            "You can review profiles below and choose who you'd like to meet."
        )
        suggestions = ["View attorneys", "Book a consultation"]
    elif any(k in text for k in ["contact", "email", "phone", "address", "location", "hours"]):
        intent = "contact_info"
        reply = (
            "You can reach us at (555) 214-0199 or hello@lexora.law. "
            "We’re available Mon–Fri, 9am–6pm, at 100 Market Street, Suite 500."
        )
        suggestions = ["Get directions", "Send an email", "Call now"]
    elif any(k in text for k in ["help", "what can you do", "how do you work"]):
        intent = "help"
        reply = HELP_TEXT
        suggestions = ["Practice areas", "Book consultation", "Contact"]
    else:
        intent = "small_talk"
        reply = (
            "I’m your AI legal assistant. Ask about practice areas, attorney bios, or say 'book a consultation'."
        )
        suggestions = ["Practice areas", "Book consultation", "Contact"]

    return VoiceResponse(reply=reply, intent=intent, suggestions=suggestions)

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
