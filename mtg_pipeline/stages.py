import os
import time
from pathlib import Path
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"

_WINDOW_START = time.time()
_TOKENS_USED = 0

def _maybe_wait(tokens: int) -> None:
    global _WINDOW_START, _TOKENS_USED
    elapsed = time.time() - _WINDOW_START
    if elapsed > 60:
        _WINDOW_START, _TOKENS_USED = time.time(), 0
        elapsed = 0
    if _TOKENS_USED + tokens > 29_000:
        wait = 60 - elapsed
        print(f"\u23F3 Waiting {wait:.1f}s to respect 30k TPM …")
        time.sleep(wait)
        _WINDOW_START, _TOKENS_USED = time.time(), 0

def _record(n: int) -> None:
    global _TOKENS_USED
    _TOKENS_USED += n

def _ask(system_prompt: str, user_content: str) -> str:
    est_in = (len(system_prompt) + len(user_content)) // 4
    est_out = 3_000
    _maybe_wait(est_in + est_out)
    for attempt in range(3):
        try:
            rsp = openai.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_content}],
                temperature=0.3,
            )
            break
        except openai.RateLimitError:
            if attempt == 2:
                raise
            print("\u23F3 Hit OpenAI rate-limit; retrying in 60s …")
            time.sleep(60)
    out = rsp.choices[0].message.content.strip()
    _record(est_in + len(out) // 4)
    return out

def run_stage(prompt_path: Path, user_content: str) -> str:
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    return _ask(prompt, user_content)
