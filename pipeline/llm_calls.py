import os
import time
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

_WINDOW_START = time.time()
_TOKENS_USED = 0


def _maybe_pause(tokens: int) -> None:
    """Pause if the rolling one-minute token use is near the limit."""
    global _WINDOW_START, _TOKENS_USED
    now = time.time()
    elapsed = now - _WINDOW_START
    if elapsed >= 60:
        _WINDOW_START = now
        _TOKENS_USED = 0
    if _TOKENS_USED + tokens > 29000:
        wait = 60 - elapsed
        if wait > 0:
            time.sleep(wait)
        _WINDOW_START = time.time()
        _TOKENS_USED = 0


def _record(tokens: int) -> None:
    global _WINDOW_START, _TOKENS_USED
    now = time.time()
    if now - _WINDOW_START >= 60:
        _WINDOW_START = now
        _TOKENS_USED = 0
    _TOKENS_USED += tokens


def _ask(msg: str) -> str:
    approx_in = len(msg) // 4
    _maybe_pause(approx_in)
    rsp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user", "content": msg},
        ],
        temperature=0.3,
    )
    out = rsp.choices[0].message.content.strip()
    _record(approx_in + len(out) // 4)
    return out


def stage_a(tk: str, base_prompt: str, transcript: str) -> str:
    prompt = f"{base_prompt}\n\nOnly produce Stage A for {tk}.\n\n{transcript}"
    return _ask(prompt)


def stage_b(tk: str, base_prompt: str, transcript: str) -> str:
    prompt = f"{base_prompt}\n\nOnly produce Stage B for {tk}.\n\n{transcript}"
    return _ask(prompt)
