import os, openai, time, re

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

# Token usage throttling
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

def stage_a(ticker: str, base_prompt: str, transcript: str) -> str:
    match = re.search(r"(.*?)STAGE B", base_prompt, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("Stage A section not found in prompt.")
    stage_a_prompt = match.group(1).strip()
    prompt = (
        f"{stage_a_prompt}\n\n"
        f"Only produce **Stage A** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)

def stage_b(ticker: str, base_prompt: str, transcript: str) -> str:
    match = re.search(r"STAGE B.*?\n+(.*?)(STAGE C|$)", base_prompt, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("Stage B section not found in prompt.")
    stage_b_prompt = match.group(1).strip()
    prompt = (
        f"{stage_b_prompt}\n\n"
        f"Only produce **Stage B** for {ticker}.\n\n"
        f"{transcript}"
    )
    return _ask(prompt)
