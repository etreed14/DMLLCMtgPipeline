import os, openai
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

def _ask(msg: str) -> str:
    rsp = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user",   "content": msg}
        ],
        temperature=0.3,
    )
    return rsp.choices[0].message.content.strip()
