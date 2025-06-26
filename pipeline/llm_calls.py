import os, openai

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

def _ask(msg: str, temperature: float = 0.3) -> str:
    rsp = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user",   "content": msg},
        ],
        temperature=temperature,
    )
    return rsp.choices[0].message.content.strip()


# ------------------------------------------------------------------
# helpers expected by run_pipeline.py
# ------------------------------------------------------------------
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
