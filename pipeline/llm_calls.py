"""
Thin helper for V9 pipeline: wraps a single ChatGPT call and exposes
stage_a() / stage_b() exactly as the old code expects.
"""

import os, openai, time

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

# Track token usage for rate-limit window
_WINDOW_START = time.time()
_TOKENS_USED  = 0

def _maybe_pause(tokens_needed: int):
    """Pause if the rolling one-minute token use is near the limit."""
    global _WINDOW_START, _TOKENS_USED
    elapsed = time.time() - _WINDOW_START

    # Reset window after 60 seconds
    if elapsed > 60:
        _WINDOW_START = time.time()
        _TOKENS_USED = 0

    # If request would exceed 30000 tokens/minute, wait
    if _TOKENS_USED + tokens_needed > 29000:
        wait_time = 60 - elapsed
        print(f"⏳ Waiting {wait_time:.1f}s to avoid token rate-limit...")
        time.sleep(wait_time)
        _WINDOW_START = time.time()
        _TOKENS_USED = 0

def _record_tokens(n: int):
    global _TOKENS_USED
    _TOKENS_USED += n

def _ask(msg: str) -> str:
    approx_in = len(msg) // 4  # Approximate input tokens
    _maybe_pause(approx_in)

    rsp = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user",   "content": msg}
        ],
        temperature=0.3,
    )
    out = rsp.choices[0].message.content.strip()
    approx_out = len(out) // 4
    _record_tokens(approx_in + approx_out)
    return out

def stage_a(ticker: str, base_prompt: str, transcript: str) -> str:
    prompt = (
        f"{base_prompt}\n\n"
        f"Only produce **Stage A** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)

def stage_b(ticker: str, base_prompt: str, transcript: str) -> str:
    prompt = (
        f"{base_prompt}\n\n"
        f"Only produce **Stage B** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)
