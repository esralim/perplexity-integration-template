"""
Perplexity API Client Wrapper

Wrapper sederhana untuk Perplexity API dengan retry logic dan rate limiting.
"""

import os
import time
import logging
import requests
from typing import Dict, Optional
from ratelimit import limits, sleep_and_retry

logger = logging.getLogger(__name__)


class PerplexityClient:
    """Client untuk Perplexity API"""
    
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        
        self.model = os.getenv("PERPLEXITY_MODEL", "sonar")
        self.temperature = float(os.getenv("PERPLEXITY_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("PERPLEXITY_MAX_TOKENS", "2000"))
        self.retry_attempts = int(os.getenv("RETRY_ATTEMPTS", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY_SECONDS", "5"))
    
    @sleep_and_retry
    @limits(calls=10, period=60)
    def _rate_limited_request(self, headers: Dict, payload: Dict) -> Dict:
        response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def query(self, prompt: str, system_prompt: str = "You are a research assistant.", temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Dict:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            "top_p": 0.9,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5
        }
        
        for attempt in range(self.retry_attempts):
            try:
                data = self._rate_limited_request(headers, payload)
                result = {
                    "content": data["choices"][0]["message"]["content"],
                    "citations": data.get("citations", []),
                    "tokens": data["usage"]["total_tokens"],
                    "model": data["model"]
                }
                logger.info(f"Perplexity API: {result['tokens']} tokens, {len(result['citations'])} sources")
                return result
            except requests.exceptions.RequestException as e:
                logger.warning(f"API failed (attempt {attempt + 1}): {str(e)}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise
        raise Exception("Query execution failed")
    
    def health_check(self) -> bool:
        try:
            result = self.query("What is 1+1?", max_tokens=10)
            return "2" in result["content"]
        except Exception:
            return False
