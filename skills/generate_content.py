"""generate_content.py
Moonshot-powered content generation skill for DepositBack agents.
"""
import json
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
    task: str = "",
    keywords: list = None,
    instructions: str = "",
    **kwargs,
):
    client = _get_client()
    keywords = keywords or []
    keyword_text = ", ".join(str(k) for k in keywords[:50])

    system_prompt = (
        "You are an expert content marketing strategist and copywriter for DepositBack, "
        "a security deposit demand letter service for US renters. "
        "You generate high-conversion, SEO-optimized content. "
        "Respond ONLY with valid JSON."
    )

    user_prompt = f"""Task: {task}

Keywords: {keyword_text}

Instructions: {instructions}

Generate a structured content brief with the following JSON format:
{{
  "title": "Content title",
  "meta_description": "SEO meta description under 160 characters",
  "content_outline": ["Section 1", "Section 2", "Section 3"],
  "key_points": ["Key point 1", "Key point 2"],
  "cta": "Call-to-action copy",
  "target_audience": "Primary audience description",
  "word_count_target": 800
}}

Return ONLY valid JSON."""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=1.0,
        max_tokens=4096,
    )

    content = resp.choices[0].message.content
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        return {
            "raw_output": content,
            "parse_error": str(e),
            "task": task,
            "keywords": keywords,
        }
