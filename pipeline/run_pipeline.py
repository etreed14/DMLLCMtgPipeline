"""
Minimal helper used by run_pipeline.py
Restores the stage_a / stage_b interface expected by V9.
"""

import os
import openai

# ------------------------------------------------------------------
# Configure OpenAI
# ------------------------------------------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"          # adjust if you prefer a different model

# ------------------------------------------------------------------
# Tiny wrapper around ChatCompletion
# ------------------------------------------------------------------
def _ask(msg: str, temperature: float = 0.3) -> str:
    """Send a single-turn prompt and return the assistant’s reply (stripped)."""
    rsp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user",   "content": msg},
        ],
        temperature=temperature,
    )
    return rsp.choices[0].message.content.strip()


# ------------------------------------------------------------------
# Public helpers expected by run_pipeline.py
# ------------------------------------------------------------------
def stage_a(ticker: str, base_prompt: str, transcript: str) -> str:
    """
    Generate Stage A (Narrative Summary) for a single ticker.
    """
    prompt = (
        f"{base_prompt}\n\n"
        f"Only produce **Stage A** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)


def stage_b(ticker: str, base_prompt: str, transcript: str) -> str:
    """
    Generate Stage B (Fact Ledger) for a single ticker.
    """
    prompt = (
        f"{base_prompt}\n\n"
        f"Only produce **Stage B** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)
