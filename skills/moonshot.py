#!/usr/bin/env python3
"""
moonshot.py
Moonshot Kimi K2.6 skill — OpenAI-compatible client.
"""
import os
from openai import OpenAI

BASE_URL = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
API_KEY = os.getenv("MOONSHOT_API_KEY")
MODEL = os.getenv("MOONSHOT_MODEL", "kimi-k2.6")

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not API_KEY:
            raise RuntimeError("MOONSHOT_API_KEY is not set")
        _client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    return _client


def run(
    system_prompt="You are a helpful assistant.",
    user_prompt="",
    temperature=1.0,
    max_tokens=4096,
    **kwargs,
):
    client = _get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content
