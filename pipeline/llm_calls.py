import os, openai
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"   # or gpt-3.5-turbo

def _ask(msg: str) -> str:
    rsp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role":"system","content":"You are MtgGPT."},
                  {"role":"user","content":msg}],
        temperature=0.3,
    )
    return rsp.choices[0].message.content.strip()

def stage_a(tk, base_prompt, transcript):
    prompt = f"{base_prompt}\n\nOnly produce Stage A for {tk}.\n\n{transcript}"
    return _ask(prompt)

def stage_b(tk, base_prompt, transcript):
    prompt = f"{base_prompt}\n\nOnly produce Stage B for {tk}.\n\n{transcript}"
    return _ask(prompt)