import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class ClaudeAPIManager:
    """Manages Claude API calls with rate limiting and token tracking"""

    def __init__(self, api_key: str, max_tokens_per_minute: int = 100000):
        self.api_key = api_key
        self.max_tokens_per_minute = max_tokens_per_minute
        self.token_usage: List[Dict] = []

    def estimate_tokens(self, text: str) -> int:
        """Rough estimate: 4 chars per token"""
        return len(text) // 4  # integer division, drops decimal

    def can_make_request(self, estimated_tokens: int) -> bool:
        """Chcek if we're within rate limits"""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)

        # filter recen tokens
        self.token_usage = [
            usage
            for usage in self.token_usage
            if usage["timestamp"] > one_minute_ago  # note: greater than one minute ago
        ]

        # calculate tokens used in last min
        self.recent_tokens = sum(usage["tokens"] for usage in self.token_usage)

        return self.recent_tokens + estimated_tokens <= self.max_tokens_per_minute

    def record_usage(self, tokens_used: int, request_type: str):
        """Record token usage for monitoring"""
        self.token_usage.append(
            {"timestamp": datetime.now(), "tokens": tokens_used, "type": request_type}
        )

    def get_usage_stats(self) -> Dict:
        """Get usage statistics for monitoring"""
        if not self.token_usage:
            return {"total_tokens": 0, "requests": 0}

        now = datetime.now()
        hour_ago = now - timedelta(hours=1)

        # tokens used within the last hour
        recent = [u for u in self.token_usage if u["timestamp"] > hour_ago]

        total_tokens = sum(u["tokens"] for u in recent)

        return {
            "total_tokens_last_hour": total_tokens,
            "requests_last_hour": len(recent),
            "average_tokens_per_request": total_tokens // len(recent) if recent else 0,
            "types": {},
            "tokens used": f"{total_tokens}/{self.max_tokens_per_minute}",
        }

    def create_batch_processor(self, requests: List[str], max_batch_size: int = 5):
        """Batch multiple requests efficiently"""
        batches = []
        current_batch = []
        current_tokens = 0

        for request in requests:
            request_tokens = self.estimate_tokens(request)

            # start new batch if adding would exceed limit
            if current_batch and (
                len(current_batch) >= max_batch_size
                or current_tokens + request_tokens > 10000
            ):
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0

            current_batch.append(request)
            current_tokens += request_tokens

        if current_batch:
            batches.append(current_batch)

        return batches
