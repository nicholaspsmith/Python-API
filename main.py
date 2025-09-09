import uvicorn
import sys
from fastapi import FastAPI, Depends, HTTPException
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
        status=ticket.status,
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
            Priority.HIGH if "urgent" in ticket.description.lower() else Priority.MEDIUM
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


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True,
    workers: int = 1
):
    """Run the Uvicorn server programatically"""
    if reload and workers > 1:
        print("Warning: --reload does not work with multiple workers")
        workers = 1
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    # Parse command line args
    import argparse
    parser = argparse.ArgumentParser(description="Run the FastAPI server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port ot bind")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers")
    parser.add_argument("--production", action="store_true", help="Run in production mode")


    args = parser.parse_args()

    if args.production:
        run_server(
            host=args.host,
            port=args.port,
            reload=False,
            workers=args.workers
        )
    else:
        run_server(
            host=args.host,
            port=args.port,
            reload=True,
            workers=1
        )
