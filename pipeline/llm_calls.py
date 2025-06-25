import os, openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def _ask(msg: str) -> str:
    rsp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are MtgGPT."},
            {"role": "user", "content": msg},
        ],
        temperature=0.3,
    )
    return rsp.choices[0].message.content.strip()


def stage_a(tk: str, base_prompt: str, transcript: str) -> str:
    prompt = f"{base_prompt}\n\nOnly produce Stage A for {tk}.\n\n{transcript}"
    return _ask(prompt)


def stage_b(tk: str, base_prompt: str, transcript: str) -> str:
    prompt = f"{base_prompt}\n\nOnly produce Stage B for {tk}.\n\n{transcript}"
    return _ask(prompt)
