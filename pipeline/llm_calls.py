import os, openai, time

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"

_WINDOW_START = time.time()
_TOKENS_USED  = 0
_MAX_TOKENS_PER_MIN = 30000
_BUFFER_OUT = 1500  # estimated output length buffer

def _maybe_pause(tokens_needed: int):
    global _WINDOW_START, _TOKENS_USED
    now = time.time()
    elapsed = now - _WINDOW_START

    # Reset window if expired
    if elapsed > 60:
        _WINDOW_START = now
        _TOKENS_USED = 0

    # If this message would push us over the 30K token limit:
    if tokens_needed > _MAX_TOKENS_PER_MIN:
        raise ValueError(f"❌ Message too large: needs {tokens_needed} tokens. GPT-4o max is 30,000/min.")

    if _TOKENS_USED + tokens_needed > _MAX_TOKENS_PER_MIN:
        wait = 60 - elapsed
        print(f"⏳ Waiting {wait:.1f}s to reset token window...")
        time.sleep(wait)
        _WINDOW_START = time.time()
        _TOKENS_USED = 0

def _record_tokens(n: int):
    global _TOKENS_USED
    _TOKENS_USED += n

def _ask(msg: str) -> str:
    approx_in = len(msg) // 4
    total_needed = approx_in + _BUFFER_OUT
    _maybe_pause(total_needed)

    print(f"📤 Sending request ({approx_in} tokens estimated input)...")

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

def stage_a(ticker: str, transcript: str) -> str:
    instructions = """
You are a summarizer. Your task is to extract a fluent, investor-style summary per company.

For each company:
• Start with a bolded header: (TICKER) — Long / Short — mm/dd/yyyy — $price
• Write full-sentence primary bullets for each material idea.
• If a bullet contains multiple points (e.g. "but", "and", ";"), split it and indent the rest.
• Push all numbers, stats, or dates into indented sub-bullets.

Use real company names or tickers mentioned in the transcript. Do not group by topic. Do not use speaker names.
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
