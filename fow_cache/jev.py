"""Minimal client for TypeSafe's Jev yes/no checks, direct or through OpenRouter.
Jev has no official SDK; this posts its documented JSON request shape."""
import json
import os
import time
import urllib.request

ENDPOINTS = {
    "typesafe": ("https://api.typesafe.ai/v1/systemone", "jev-latest"),
    "openrouter": ("https://openrouter.ai/api/alpha/decisions", "~typesafe/jev-latest"),
}


class JevClient:
    """noul(state, instructions) -> probability of yes, 0 to 1.

    Reads TYPESAFE_API_KEY, else OPENROUTER_API_KEY, unless api_key/provider are given."""

    def __init__(self, api_key=None, provider=None, timeout=30, retries=4):
        if provider is None:
            provider = "typesafe" if os.environ.get("TYPESAFE_API_KEY") else "openrouter"
        self.endpoint, self.model = ENDPOINTS[provider]
        self.api_key = api_key or os.environ.get("TYPESAFE_API_KEY" if provider == "typesafe" else "OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("Jev needs TYPESAFE_API_KEY or OPENROUTER_API_KEY")
        self.timeout, self.retries = timeout, retries

    def noul(self, state, instructions):
        body = {"model": self.model, "state": state,
                "questions": {"same_answer": {"type": "noul", "instructions": instructions}}}
        req = urllib.request.Request(self.endpoint, data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return float(json.load(r)["answers"]["same_answer"]["noul"])
            except Exception as e:  # transient network/rate errors: back off and retry
                if attempt == self.retries:
                    raise RuntimeError(f"Jev request failed: {e}") from e
                time.sleep(2 ** attempt)
