import re

# Accept either:
#   • A 2-to-5-letter ticker (AAPL, MSFT, NVDA, etc.)
#   • The same ticker with a leading $ ($NVDA, $TSLA, etc.)
#   • A handful of full company names (case-insensitive) so transcripts that
#     spell out “Apple” or “Nvidia” are still captured.
_TICKER_RE = re.compile(
    r"(?:\$?[A-Z]{2,5}|Apple|Microsoft|Nvidia|Google|Amazon|Tesla|Cisco|Dell)",
    re.I,
)

def extract_tickers(text: str) -> list[str]:
    """
    Return a sorted list of unique symbols / names found in the transcript.
    Leading '$' is stripped; output is upper-cased to normalise.
    """
    return sorted({m.group(0).lstrip("$").upper() for m in _TICKER_RE.finditer(text)})
