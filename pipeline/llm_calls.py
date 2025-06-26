"""
Thin helper for V9 pipeline: wraps a single ChatGPT call and exposes
stage_a() / stage_b() exactly as the old code expects.
"""

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"           # or any model you prefer


def _ask(msg: str, *, temperature: float = 0.3) -> str:
    """One-shot ChatCompletion call (works with openai-python ≥ 1.0)."""
    rsp = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user",   "content": msg},
        ],
        temperature=temperature,
    )
    return rsp.choices[0].message.content.strip()


# ------------------------------------------------------------------ #
#  Public helpers that run_pipeline.py imports
# ------------------------------------------------------------------ #
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
