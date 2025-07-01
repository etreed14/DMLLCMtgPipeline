"""
llm_calls.py  ·  V9 helper (prompt slices)

Exposes:
    stage_a(prompt_slice, transcript)
    stage_b(prompt_slice, transcript)
    stage_c(prompt_slice, stage_a_text, stage_b_text)

Handles:
    • 30 000-TPM rolling window guard
    • Automatic retry on OpenAI 429
"""

import os, time
from pathlib import Path
import openai
from openai import RateLimitError

# ─────────────────────────────  OpenAI  ──────────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"

# ──────────────────────  Rolling TPM guard  ──────────────────────────
_WINDOW_START, _TOKENS_USED = time.time(), 0

def _maybe_pause(tokens_needed: int) -> None:
    """Block if adding tokens_needed would exceed 30 k tokens / minute."""
    global _WINDOW_START, _TOKENS_USED
    elapsed = time.time() - _WINDOW_START
    if elapsed > 60:
        _WINDOW_START, _TOKENS_USED = time.time(), 0
        elapsed = 0
    if _TOKENS_USED + tokens_needed > 29_000:          # 1 k headroom
        wait = 60 - elapsed
        print(f"⏳ Waiting {wait:.1f}s to respect 30 k TPM …")
        time.sleep(wait)
        _WINDOW_START, _TOKENS_USED = time.time(), 0

def _record(n: int) -> None:
    global _TOKENS_USED
    _TOKENS_USED += n

# ─────────────────────────  Core wrapper  ────────────────────────────
def _ask(system_prompt: str, user_prompt: str) -> str:
    est_in  = (len(system_prompt) + len(user_prompt)) // 4
    est_out = 3_000                       # generous reply budget
    _maybe_pause(est_in + est_out)

    for attempt in range(3):
        try:
            rsp = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.3,
            )
            break
        except RateLimitError:
            if attempt == 2:
                raise
            print("⏳ Hit OpenAI rate-limit; retrying in 60 s …")
            time.sleep(60)

    out = rsp.choices[0].message.content.strip()
    _record(est_in + len(out) // 4)
    return out

# ────────────────────────  Public helpers  ───────────────────────────
def stage_a(prompt_slice: str, transcript: str) -> str:
    """Return Stage A narrative using the prompt slice supplied."""
    return _ask(prompt_slice, transcript)

def stage_b(prompt_slice: str, transcript: str) -> str:
    """Return Stage B fact ledger using the prompt slice supplied."""
    return _ask(prompt_slice, transcript)

def stage_c(prompt_slice: str, stage_a_text: str, stage_b_text: str) -> str:
    """Return Stage C HTML using the prompt slice supplied."""
    user = f"STAGE_A:\n{stage_a_text.strip()}\n\nSTAGE_B:\n{stage_b_text.strip()}"
    return _ask(prompt_slice, user)
