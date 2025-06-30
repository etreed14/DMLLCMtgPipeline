"""
llm_calls.py  ·  V9 helper (3-file prompt version)

• Loads PromptV9a / PromptV9b / PromptV9c once at import time
• Exposes:
      stage_a(prompt_A, transcript)
      stage_b(prompt_B, transcript)
      stage_c(prompt_C, html)   # optional
• Guards against 30 000-TPM bursts and auto-retries on 429
"""

import os, time
from pathlib import Path
import openai
from openai import RateLimitError

# ───────────────────────────  OpenAI  ────────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY") or "YOUR_KEY_HERE"
MODEL = "gpt-4o"

# ──────────────────────  Load prompt slices  ─────────────────────
PROMPT_A = Path("prompts/MtgGPTPromptV9a.txt").read_text()
PROMPT_B = Path("prompts/MtgGPTPromptV9b.txt").read_text()
PROMPT_C = Path("prompts/MtgGPTPromptV9c.txt").read_text()

# ───────────────  Simple rolling TPM rate-limit guard  ───────────
_WINDOW_START, _TOKENS_USED = time.time(), 0
def _maybe_pause(tokens_needed: int):
    """Pause if adding tokens_needed would breach 30 000-TPM."""
    global _WINDOW_START, _TOKENS_USED
    elapsed = time.time() - _WINDOW_START
    if elapsed > 60:
        _WINDOW_START, _TOKENS_USED = time.time(), 0
    if _TOKENS_USED + tokens_needed > 29_000:    # leave 1k headroom
        wait = 60 - elapsed
        print(f"⏳ Waiting {wait:.1f}s to respect 30 k TPM …")
        time.sleep(max(wait, 0))
        _WINDOW_START, _TOKENS_USED = time.time(), 0
def _record(n: int):
    global _TOKENS_USED
    _TOKENS_USED += n

# ─────────────────────  Core call helper  ────────────────────────
def _ask(system_prompt: str, user_content: str) -> str:
    """Robust wrapper around Chat Completions with TPM guard + retry."""
    est_in  = (len(system_prompt) + len(user_content)) // 4
    est_out = 3000          # reserve 3 000-token reply worst-case
    _maybe_pause(est_in + est_out)

    for attempt in range(3):
        try:
            rsp = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_content},
                ],
                temperature=0.3,
            )
            break  # success
        except RateLimitError as e:
            if attempt == 2:
                raise
            wait = 60
            print("⏳ hit TPM limit; sleeping 60 s …")
            time.sleep(wait)

    out = rsp.choices[0].message.content.strip()
    _record(est_in + len(out) // 4)
    return out

# ────────────────────────  Public API  ───────────────────────────
def stage_a(prompt: str, transcript: str) -> str:
    return _ask(prompt, transcript)

def stage_b(prompt: str, transcript: str) -> str:
    return _ask(prompt, transcript)

def stage_c(prompt_c: str, assembled_html: str) -> str:
    """Optional: wrap or post-process HTML via GPT."""
    return _ask(prompt_c, assembled_html)
