"""
Thin helper for V9 pipeline: wraps a single ChatGPT call and exposes
stage_a() / stage_b() exactly as the old code expects.
"""

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def _ask(msg: str) -> str:
    rsp = openai.chat.completions.create(
        model="gpt-4o",  # or "gpt-4o-mini" if you prefer
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user", "content": msg}
        ],
        temperature=0.3,
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
