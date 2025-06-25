"""
pipeline/run_pipeline.py
Generate Stage A + Stage B for every ticker (or company name) found
in the newest transcript, build the V9-style HTML, and save it under
data/summaries/InvestmentSummary_YYYY-MM-DD.html
"""

import datetime
from pathlib import Path
from utils import extract_tickers
from llm_calls import stage_a, stage_b
from formatter import split_and_indent, build_block, build_html

# ------------------------------------------------------------------ #
# 1. Read prompt and the ONLY .txt transcript in data/transcripts/
# ------------------------------------------------------------------ #
BASE_PROMPT = Path("prompts/MtgGPTPromptV9.txt").read_text()

transcripts = list(Path("data/transcripts").glob("*.txt"))
if not transcripts:
    raise SystemExit("🚫 No transcript found in data/transcripts/")
if len(transcripts) > 1:
    print("⚠️  Multiple transcripts found; using first alphabetically.")
TRANSCRIPT = transcripts[0].read_text()

# ------------------------------------------------------------------ #
# 2. Extract tickers / names
# ------------------------------------------------------------------ #
tickers = extract_tickers(TRANSCRIPT)
if not tickers:
    tickers = ["GENERIC"]          # fallback so we always produce an HTML

# ------------------------------------------------------------------ #
# 3. Build blocks (Stage A + Stage B) per ticker
# ------------------------------------------------------------------ #
blocks = []
for tk in tickers:
    print(f"🟢 Processing {tk} …")
    a_raw = stage_a(tk, BASE_PROMPT, TRANSCRIPT)
    b_raw = stage_b(tk, BASE_PROMPT, TRANSCRIPT)
    blocks.append(build_block(tk, split_and_indent(a_raw), b_raw))

# ------------------------------------------------------------------ #
# 4. Write HTML
# ------------------------------------------------------------------ #
html = build_html(blocks)
out_path = Path("data/summaries") / f"InvestmentSummary_{datetime.date.today()}.html"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(html, encoding="utf-8")
print("✔ saved", out_path)