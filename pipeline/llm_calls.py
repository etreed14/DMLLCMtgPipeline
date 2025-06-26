#  ── pipeline/llm_calls.py ────────────────────────────────────────────────
import os, openai

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"          # swap for any other model you prefer


def _ask(msg: str, temperature: float = 0.3) -> str:
    """Single-turn helper around ChatCompletion."""
    rsp = openai.ChatCompletion.create(        # ← newer SDK spellings also work
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user",   "content": msg},
        ],
        temperature=temperature,
    )
    return rsp.choices[0].message.content.strip()


# ------------------------------------------------------------------ #
# V9-style public helpers expected by run_pipeline.py
# ------------------------------------------------------------------ #
def stage_a(ticker: str, base_prompt: str, transcript: str) -> str:
    """
    Generate the **Stage A – narrative summary**.
    `ticker` is ignored in the new single-pass pipeline, but we keep the
    parameter so run_pipeline can call the function unchanged.
    """
    prompt = (
        f"{base_prompt}\n\n"
        f"Only produce **Stage A** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)


def stage_b(ticker: str, base_prompt: str, transcript: str) -> str:
    """
    Generate the **Stage B – fact ledger**.
    """
    prompt = (
        f"{base_prompt}\n\n"
        f"Only produce **Stage B** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)
