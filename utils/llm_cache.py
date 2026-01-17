"""
LLM Response Caching - verhindert wiederholte API-Aufrufe
"""

import json
import hashlib
import os
from typing import Optional, Any
from pathlib import Path

CACHE_DIR = Path("./data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def hash_prompt(prompt: str) -> str:
    """Hash eines Prompts für Caching."""
    return hashlib.md5(prompt.encode()).hexdigest()[:16]


def get_cached_response(prompt: str) -> Optional[str]:
    """Hole gecachte Response wenn vorhanden."""
    cache_key = hash_prompt(prompt)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                data = json.load(f)
                return data.get("response")
        except:
            pass
    
    return None


def save_cached_response(prompt: str, response: str):
    """Speichere Response im Cache."""
    cache_key = hash_prompt(prompt)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    try:
        with open(cache_file, 'w') as f:
            json.dump({
                "prompt_hash": cache_key,
                "response": response
            }, f)
    except:
        pass  # Silent fail - caching is optional


def clear_cache():
    """Lösche alle gecachten Responses."""
    try:
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()
    except:
        pass
