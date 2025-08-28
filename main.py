from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from rate_limiter import RateLimiter

app = FastAPI()

limiter = RateLimiter(max_requests=5, window_seconds=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
  # use IP as client identifier
  client_id = request.client.host

  if not limiter.is_allowed(client_id):
    return JSONResponse(
      status_code=429,
      content={"detail": "Rate limit exceeded. Try again later."},
      headers={"X-Requests-Remaining": "0"}
    )
  
  response = await call_next(request)
  # add header showing remaining requests
  response.headers["X-Requests-Remaining"] = str(
    limiter.requests_remaining(client_id)
  )
  return response;

class Ticket(BaseModel):
  id: Optional[int] = None
  title: str
  description: str
  priority: str # "low", "medium", "high", "critical"
  status: str = "open"

tickets = []

# Uvicorn contains built-in route
# /docs
# Which contains all possible endpoints

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