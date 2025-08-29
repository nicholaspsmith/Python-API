import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

# from rate_limiter import RateLimiter
from claude_manager import ClaudeAPIManager

app = FastAPI()

# limiter = RateLimiter(max_requests=5, window_seconds=60)

# @app.middleware("http")
# async def rate_limit_middleware(request: Request, call_next):
#   # use IP as client identifier
#   client_id = request.client.host

#   if not limiter.is_allowed(client_id):
#     return JSONResponse(
#       status_code=429,
#       content={"detail": "Rate limit exceeded. Try again later."},
#       headers={"X-Requests-Remaining": "0"}
#     )

#   response = await call_next(request)
#   # add header showing remaining requests
#   response.headers["X-Requests-Remaining"] = str(
#     limiter.requests_remaining(client_id)
#   )
#   return response;

claude = ClaudeAPIManager(api_key="", max_tokens_per_minute=10000)


class Ticket(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    priority: str  # "low", "medium", "high", "critical"
    status: str = "open"


tickets = []

# Uvicorn built-in route
# @app.get("/docs")


@app.get("/")
def read_root():
    return {"message": "Ticket tracking system running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/tickets")
def create_ticket(ticket: Ticket):
    ticket.id = len(tickets) + 1
    tickets.append(ticket)
    return ticket


@app.get("/tickets")
def get_tickets():
    return tickets


@app.post("/analyze-ticket")
async def analyze_ticket(ticket: Ticket):
    """Analyze ticket priority and suggest response"""

    prompt = f"Analyze this support ticket:\nTitle: {ticket.title}\nDescription: {ticket.description}"
    # Add 500 tokens to allow space for Claude's response
    estimated_tokens = claude.estimate_tokens(prompt) + 500

    if not claude.can_make_request(estimated_tokens):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Claude API rate limit reached. Try again later.",
                "stats": claude.get_usage_stats(),
            },
        )

    # Simulate claude api call (todo: implement actual claude api call)
    claude.record_usage(estimated_tokens, "ticket_analysis")

    # return mocked response (todo: implement actual response)
    return {
        "suggested_priority": (
            "high" if "urgent" in ticket.description.lower() else "medium"
        ),
        "suggested_response": f"Thank you for contacting support about '{ticket.title}'. We will get back to you shortly.",
        "tokens_used": estimated_tokens,
        "stats": claude.get_usage_stats(),
    }


@app.post("/analyze-tickets")
async def analyze_tickets(tickets: List[Ticket]):
    """Batch analyze tickets"""
    prompts = []
    for ticket in tickets:
        prompts.append(
            f"Analyze this support ticket:\nTitle: {ticket.title}\nDescription: {ticket.description}"
        )
    batches = claude.create_batch_processor(prompts, max_batch_size=3)
    responses = []
    for num, batch in enumerate(batches):
        for prompt in batch:
                estimated_tokens = claude.estimate_tokens(prompt) + 500
                if not claude.can_make_request(estimated_tokens):
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Claude API rate limit reached. Try again later.",
                            "stats": claude.get_usage_stats(),
                        },
                    )

                # Simulate claude api call (todo: implement actual claude api call)
                claude.record_usage(estimated_tokens, "ticket_analysis")

                # return mocked response (todo: implement actual response)
                responses.append({
                    "batch": num,
                    "suggested_response": f"Thank you for contacting support. We will get back to you shortly.",
                    "tokens_used": estimated_tokens,
                    "stats": claude.get_usage_stats(),
                })
    return responses
