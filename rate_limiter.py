from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List

class RateLimiter:
  def __init__(self, max_requests: int = 10, window_seconds: int = 60):
    self.max_requests = max_requests
    self.window = timedelta(seconds=window_seconds)
    self.requests: Dict[str, List[datetime]] = defaultdict(list)

  def is_allowed(self, client_id: str) -> bool:
    now = datetime.now()
    # filter out reqeusts older than window_seconds
    self.requests[client_id] = [
      req_time for req_time in self.requests[client_id]
      if now - req_time < self.window
    ]

    # check if under number of max requests
    if len(self.requests[client_id]) < self.max_requests:
      self.requests[client_id].append(now)
      return True
    return False
  
  def requests_remaining(self, client_id: str) -> int:
    # number of requests left in current window
    now = datetime.now()
    self.requests[client_id] = [
      req_time for req_time in self.requests[client_id]
      if now - req_time < self.window
    ]
    return self.max_requests - len(self.requests[client_id])