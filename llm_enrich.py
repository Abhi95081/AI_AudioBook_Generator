from __future__ import annotations

import os
from typing import Optional, Literal

from utils import chunk_text

# Optional OpenAI import
try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore

# Optional Gemini import
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except Exception:
    genai = None
    HAS_GEMINI = False


# Enhanced prompts for audiobook narration
AUDIOBOOK_PROMPT = """You are an expert audiobook editor. Rewrite the following text to make it perfect for audiobook narration:

1. Fix any OCR errors or typos
2. Improve sentence flow and pacing for spoken narration
3. Add natural pauses where appropriate (use punctuation)
4. Make the language more engaging and listener-friendly
5. Keep the original meaning and key information intact
6. Remove awkward phrasing that sounds unnatural when spoken

Output only the improved text, no explanations."""

SIMPLE_PROMPT = (
    "You are a helpful assistant. Improve clarity and fix obvious OCR errors "
    "without changing meaning. Keep the output concise but faithful."
)


LLMProvider = Literal["openai", "gemini", "auto"]


def _openai_client() -> Optional["OpenAI"]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None
    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception:
        return None


def _gemini_client():
    """Initialize Gemini client if API key is available."""
    if not HAS_GEMINI:
        return None
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-pro')
    except Exception:
        return None


def enrich_text(
    text: str, 
    model: Optional[str] = None, 
    max_chars: int = 4000,
    provider: LLMProvider = "auto",
    audiobook_mode: bool = True,
) -> str:
    """
    Enrich text using LLM (OpenAI, Gemini, or auto-detect).
    
    Args:
        text: Input text to enrich
        model: Specific model to use (e.g., "gpt-4o-mini" or "gemini-pro")
        max_chars: Maximum characters per chunk
        provider: LLM provider - "openai", "gemini", or "auto" (tries Gemini first, then OpenAI)
        audiobook_mode: Use enhanced audiobook narration prompt
    
    Returns:
        Enriched text, or original if no LLM available
    """
    text = text or ""
    if not text.strip():
        return text
    
    prompt = AUDIOBOOK_PROMPT if audiobook_mode else SIMPLE_PROMPT
    
    # Auto-select provider
    if provider == "auto":
        if HAS_GEMINI and os.getenv("GOOGLE_API_KEY"):
            provider = "gemini"
        elif OpenAI and os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            return text  # No LLM available
    
    chunks = chunk_text(text, max_chars=max_chars)
    outputs = []
    
    if provider == "gemini":
        client = _gemini_client()
        if client is None:
            return text
        
        for ch in chunks:
            try:
                response = client.generate_content(f"{prompt}\n\nText:\n{ch}")
                outputs.append(response.text or ch)
            except Exception as e:
                print(f"Gemini error: {e}")
                outputs.append(ch)
    
    elif provider == "openai":
        client = _openai_client()
        if client is None:
            return text
        
        model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        for ch in chunks:
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": ch},
                    ],
                    temperature=0.3,
                )
                outputs.append(resp.choices[0].message.content or ch)
            except Exception as e:
                print(f"OpenAI error: {e}")
                outputs.append(ch)
    
    return "\n".join(outputs)
