from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import Enum
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db, TicketModel, Priority, TicketStatus
from pydantic import BaseModel
from datetime import datetime
from claude_manager import ClaudeAPIManager
from analytics import TicketAnalytics

app = FastAPI(title="Ticket System")

claude = ClaudeAPIManager(api_key="", max_tokens_per_minute=10000)

analytics = TicketAnalytics()

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    status: TicketStatus
    created_at: datetime
    claude_suggested_priority: Optional[Priority] = None
    claude_suggested_response: Optional[str] = None

    # Tell Pydantic to work with SQLAlchemy models
    class Config:
        from_attributes = True

# Uvicorn built-in route
# @app.get("/docs")


@app.get("/")
def read_root():
    return {"message": "Ticket tracking system running"}


@app.post("/tickets", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    db_ticket = TicketModel(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return db_ticket


@app.get("/tickets", response_model=List[TicketResponse])
def get_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tickets = db.query(TicketModel).offset(skip).limit(limit).all()
    return tickets

@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.put("/tickets/{ticket_id}/analyze", response_model=TicketResponse)
async def analyze_and_update_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Analyze ticket with Claude & save result to db"""
    ticket = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Claude analysis logic ##TODO
    prompt = f"Analyze: {ticket.title} - {ticket.description}"
    estimated_tokens = claude.estimate_tokens(prompt) + 500

    if claude.can_make_request(estimated_tokens):
        # simulate Claude response
        ticket.claude_suggested_priority = (
            Priority.HIGH if "urgent" in ticket.description.lower()
            else Priority.MEDIUM
        )
        ticket.claude_suggested_response = "Thank you for contacting support."
        ticket.tokens_used = estimated_tokens

        db.commit()
        db.refresh(ticket)

        claude.record_usage(estimated_tokens, "ticket_analysis")

    return ticket

@app.get("/analytics/priority")
def get_priority_analytics():
    """Get priority distribution analytics"""
    return analytics.analyze_priority_distribution()

@app.get("/analytics/tokens")
def get_token_analytics():
    """Get Claude token usage analytics"""
    return analytics.analyze_token_usage()

@app.get("/analytics/timeline")
def get_timeline_analytics():
    """Get ticket creation timeline analytics"""
    return analytics.time_series_analysis()

@app.get("/analytics/summary")
def get_summary_analytics():
    """Get comprehensive summary statistics"""
    return analytics.get_summary_statistics()

# Initialize uvicorn server when main.py is run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)