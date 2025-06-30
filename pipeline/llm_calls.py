"""
llm_calls.py  –  V9 helper (3-file prompt version)

• Loads PromptV9a / PromptV9b / PromptV9c once at import time
• Exposes:
      stage_a(prompt_A, transcript)
      stage_b(prompt_B, transcript)
      stage_c(prompt_C, assembled_html)   # optional
• Guards against 30 000-token-per-minute bursts.
"""

import os, time, openai
from pathlib import Path

# ───────────────────────────  OpenAI  ────────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"           # change here if you need a different model

# ──────────────────────  Load prompt slices  ─────────────────────
PROMPT_A = Path("prompts/MtgGPTPromptV9a.txt").read_text()
PROMPT_B = Path("prompts/MtgGPTPromptV9b.txt").read_text()
PROMPT_C = Path("prompts/MtgGPTPromptV9c.txt").read_text()   # only if you need it

# ───────────────  Simple rolling TPM rate-limit guard  ───────────
_WINDOW_START, _TOKENS_USED = time.time(), 0
def _maybe_pause(tokens_needed: int):
    global _WINDOW_START, _TOKENS_USED
    elapsed = time.time() - _WINDOW_START
    if elapsed > 60:
        _WINDOW_START, _TOKENS_USED = time.time(), 0
    if _TOKENS_USED + tokens_needed > 29_000:
        wait = 60 - elapsed
        print(f"⏳ Waiting {wait:.1f}s to respect 30 k tokens/minute…")
        time.sleep(wait)
        _WINDOW_START, _TOKENS_USED = time.time(), 0
def _record(n: int):
    global _TOKENS_USED
    _TOKENS_USED += n

# ─────────────────────  Core call helper  ────────────────────────
def _ask(system_prompt: str, user_content: str) -> str:
    """Low-level wrapper around the Chat Completions API."""
    in_tok = len(system_prompt) // 4 + len(user_content) // 4
    _maybe_pause(in_tok)

    rsp = openai.chat.completions.create(
        model=MODEL,
        messages=[
            # put ALL instructions here
            {"role": "system", "content": system_prompt},
            # put ONLY the transcript (or question) here
            {"role": "user",   "content": user_content},
        ],
        temperature=0.3,
    )
    out = rsp.choices[0].message.content.strip()
    _record(in_tok + len(out) // 4)
    return out
# ────────────────────────  Public API  ───────────────────────────
def stage_a(prompt_A: str, transcript: str) -> str:
    """Return Stage A narrative for this transcript chunk."""
    return _ask(f"{prompt_A}\n\n{transcript}")

def stage_b(prompt_B: str, transcript: str) -> str:
    """Return Stage B fact ledger for this transcript chunk."""
    return _ask(f"{prompt_B}\n\n{transcript}")

def stage_c(prompt_C: str, assembled_html: str) -> str:
    """
    (Optional) If you ever want GPT to wrap/finish the HTML, call this.
    The current pipeline builds HTML locally, so you may not need it.
    """
    return _ask(f"{prompt_C}\n\n{assembled_html}")
