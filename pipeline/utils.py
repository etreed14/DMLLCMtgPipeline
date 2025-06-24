import re
def extract_tickers(text: str) -> list[str]:
    return sorted(set(re.findall(r"\b[A-Z]{2,5}\b", text)))