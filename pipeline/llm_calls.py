import os
from vendor_openai import chat_completion

def _ask(msg: str) -> str:
    rsp = chat_completion(
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user", "content": msg},
        ],
        model="gpt-4o",
        temperature=0.3,
    )
    return rsp["choices"][0]["message"]["content"].strip()


def stage_a(tk: str, base_prompt: str, transcript: str) -> str:
    return _ask(f"{base_prompt}\n\nOnly produce Stage A for ({tk}).\n\n{transcript}")


def stage_b(tk: str, base_prompt: str, transcript: str) -> str:
    return _ask(f"{base_prompt}\n\nOnly produce Stage B for ({tk}).\n\n{transcript}")

