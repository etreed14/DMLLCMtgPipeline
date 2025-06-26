import os, openai, time

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"

_WINDOW_START = time.time()
_TOKENS_USED  = 0

def _maybe_pause(tokens_needed: int):
    global _WINDOW_START, _TOKENS_USED
    now = time.time()
    elapsed = now - _WINDOW_START

    # Reset the window after 60s
    if elapsed > 60:
        _WINDOW_START = now
        _TOKENS_USED = 0

    # If the next call would exceed 30k, pause until the window resets
    if _TOKENS_USED + tokens_needed >= 29900:
        wait = 60 - elapsed
        print(f"⏳ Hit token cap. Waiting {wait:.1f}s...")
        time.sleep(wait)
        _WINDOW_START = time.time()
        _TOKENS_USED = 0

def _record_tokens(n: int):
    global _TOKENS_USED
    _TOKENS_USED += n

def _ask(msg: str) -> str:
    import openai
    import time

    approx_in = len(msg) // 4
    buffer_out = 2000  # reserve generous buffer
    total_needed = approx_in + buffer_out

    _maybe_pause(total_needed)

    while True:
        try:
            rsp = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are MtgGPT."},
                    {"role": "user",   "content": msg}
                ],
                temperature=0.3,
            )
            break  # success, exit retry loop
        except openai.RateLimitError as e:
            print("⚠ Rate limit hit. Waiting 60s...")
            time.sleep(60)
            _reset_window()

    out = rsp.choices[0].message.content.strip()
    actual_out = len(out) // 4
    _record_tokens(approx_in + actual_out)
    return out

def _reset_window():
    global _WINDOW_START, _TOKENS_USED
    _WINDOW_START = time.time()
    _TOKENS_USED = 0

def stage_a(ticker: str, transcript: str) -> str:
    instructions = """
You are a summarizer. Your task is to extract a fluent, investor-style summary per company.

For each company:
• Start with a bolded header: (TICKER) — Long / Short — mm/dd/yyyy — $price
• Write full-sentence primary bullets for each material idea.
• If a bullet contains multiple points (e.g. "but", "and", ";"), split it and indent the rest.
• Push all numbers, stats, or dates into indented sub-bullets.

Use real company names or tickers mentioned in the transcript. Group bullets clearly by company. Do not group by topic like “Activism” or “AI”. No speaker names or summaries.
"""
    return _ask(f"{instructions.strip()}\n\n{transcript}")

def stage_b(ticker: str, transcript: str) -> str:
    instructions = """
You are a fact collector. Your task is to extract all remaining financials, metrics, quotes, and numeric insights per company.

Format:
(TICKER) — Facts
──────────────────────
• Create buckets like Financial, Tech, Risks, Installed Base, Catalysts, etc.
• Use nested bullets to organize ideas (stat → detail → micro-detail)
• Include ALL facts, even if they seem redundant. Do not editorialize.
• Only use companies actually mentioned in the transcript.

Return only the fact ledger.
"""
    return _ask(f"{instructions.strip()}\n\n{transcript}")
