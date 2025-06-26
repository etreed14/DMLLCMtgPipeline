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
    global _WINDOW_START, _TOKENS_USED
    elapsed = time.time() - _WINDOW_START

    if elapsed > 60:
        _WINDOW_START = time.time()
        _TOKENS_USED = 0

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
    approx_in = len(msg) // 4
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

# -------------------------------------------------------------------------
# Public functions: run Stage A and Stage B by slicing the prompt correctly
# -------------------------------------------------------------------------

def stage_a(ticker: str, base_prompt: str, transcript: str) -> str:
    # Get only the Stage A section of the prompt
    stage_a_prompt = base_prompt.split("STAGE B")[0].strip()

    prompt = (
        f"{stage_a_prompt}\n\n"
        f"Only produce **Stage A** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)

def stage_b(ticker: str, base_prompt: str, transcript: str) -> str:
    # Get the Stage B section between B and C
    stage_b_prompt = base_prompt.split("STAGE B —")[1].split("STAGE C")[0].strip()

    prompt = (
        f"{stage_b_prompt}\n\n"
        f"Only produce **Stage B** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)
