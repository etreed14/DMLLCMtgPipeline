import os, openai, time

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"

_WINDOW_START = time.time()
_TOKENS_USED = 0

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

# ——————————————————————————————————————————————
# Embedded prompt logic for V9 format: no external .txt
# ——————————————————————————————————————————————

_STAGE_A_PROMPT = """Craft a fluent, investor-style pitch for **each company**.

Header line (bold):
  **(TICKER) — Long / Short — mm/dd/yyyy — $price**

• Keep adding primary bullets until every material idea is voiced
  (edge, catalysts, valuation math, debate, risks, etc).  
• One idea per bullet — natural prose.
• If a bullet contains multiple ideas (joined by ";", " and ", or " but"), split it.
  If the second idea depends on the first, indent it one level deeper.
• Push all numbers / % / $ / dates to indented sub-bullets.
• Keep your tone punchy but professional.
"""

_STAGE_B_PROMPT = """Build an exhaustive fact ledger for **each company**.

Company block header:
  (TICKER) — Facts
  ──────────────────────

• Create whatever buckets are needed (Financial, Edge/Tech, AI Use Cases, etc.)
• Unlimited nesting: bullets → subpoenas → sub-sub-bullets
• Do NOT drop any details — include every stat, quote, metric, or claim.
• Do not merge with Stage A — treat this as a parallel ledger of all unused data.
"""

# ——————————————————————————————————————————————
# Stage A / B with embedded prompts
# ——————————————————————————————————————————————

def stage_a(ticker: str, transcript: str) -> str:
    msg = f"{_STAGE_A_PROMPT}\n\nOnly produce **Stage A** for {ticker}.\n\n{transcript}"
    return _ask(msg)

def stage_b(ticker: str, transcript: str) -> str:
    msg = f"{_STAGE_B_PROMPT}\n\nOnly produce **Stage B** for {ticker}.\n\n{transcript}"
    return _ask(msg)
