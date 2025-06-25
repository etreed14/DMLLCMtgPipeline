import os
import requests

API_URL = "https://api.openai.com/v1/chat/completions"

def chat_completion(messages, model="gpt-4o", temperature=0.3):
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    resp = requests.post(API_URL, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    return resp.json()
