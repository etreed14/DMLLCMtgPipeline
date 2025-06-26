import os, openai, time

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

_WINDOW_START = time.time()
_TOKENS_USED  = 0

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
            {"role": "user", "content": msg}
        ],
        temperature=0.3,
    )
    out = rsp.choices[0].message.content.strip()
    approx_out = len(out) // 4
    _record_tokens(approx_in + approx_out)
    return out

def stage_a(ticker: str, base_prompt: str, transcript: str) -> str:
    stage_a_prompt = """STAGE A — NARRATIVE SUMMARY (clean bullets)
────────────────────────────────────────────────────────────
Goal: craft a fluent, investor‑style pitch for **each company**.

Header line (bold):
  **(TICKER) — Long / Short — mm/dd/yyyy — $price**

• Keep adding primary bullets until every material idea is voiced
  (edge, catalysts, valuation maths, debate, risks, colour).  
• One idea per bullet; natural prose.  
• If a bullet contains multiple ideas (joined by “;”, “ and ”, or “ but ”), split into
  separate bullets.  If the second idea depends on the first, indent it one level.
• Push ALL numbers / % / $ / dates to indented sub‑bullets.

Print every company’s section, then stop."""
    return _ask(f"{stage_a_prompt}\n\n{transcript}")

def stage_b(ticker: str, base_prompt: str, transcript: str) -> str:
    stage_b_prompt = """STAGE B — FACT LEDGER (Quick‑stats source)
────────────────────────────────────────────────────────────
Goal: capture **all** remaining stats / metrics / quotes, grouped by company.

Loop over every ticker seen in Stage A:

  (TICKER) — Facts
  ──────────────────────
  • Create whatever buckets are needed (Financial, Edge/Tech, AI Use Cases, …).
  • Unlimited nesting — NOTHING is dropped.
  • Do *not* rewrite or merge with Stage A.

Print the full fact ledger and stop."""
    return _ask(f"{stage_b_prompt}\n\n{transcript}")
