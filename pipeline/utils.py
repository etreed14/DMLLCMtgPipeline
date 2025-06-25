import re

# Accept either:
#   • 2-to-5-letter tickers (AAPL, MSFT, NVDA, etc.)
#   • Optional leading $ ($NVDA)
#   • Common full company names (case-insensitive)
_TICKER_RE = re.compile(
    r"(?:\$?[A-Z]{2,5}|Apple|Microsoft|Nvidia|Google|Amazon|Tesla|Cisco|Dell)",
    re.I,
)

def extract_tickers(text: str) -> list[str]:
    """
    Return a sorted list of unique symbols / names found in the transcript.
    Leading '$' is stripped; output is upper-cased so “Apple” → “APPLE”.
    """
    return sorted({m.group(0).lstrip("$").upper()
                   for m in _TICKER_RE.finditer(text)})