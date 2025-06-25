# pipeline/run_pipeline.py  ✨ totally self-contained ✨
import datetime
from pathlib import Path

from utils import extract_tickers
from llm_calls import stage_a, stage_b          # <- must already exist
from formatter import split_and_indent, build_block, build_html

BASE_PROMPT = Path("prompts/MtgGPTPromptV9.txt").read_text()
TRANSCRIPT  = Path("data/transcripts/dinnerTranscript.txt").read_text()

# --------------------------------------------------------------------------
# 1) Decide which symbols we’re going to summarise
# --------------------------------------------------------------------------
tickers = extract_tickers(TRANSCRIPT)
if not tickers:                         # fallback if none were found
    tickers = ["GENERAL"]               # treat whole transcript as one company

# --------------------------------------------------------------------------
# 2) Run Stage A & Stage B for each symbol
# --------------------------------------------------------------------------
blocks: list[str] = []
for tk in tickers:
    a_raw = stage_a(tk, BASE_PROMPT, TRANSCRIPT)
    b_raw = stage_b(tk, BASE_PROMPT, TRANSCRIPT)
    blocks.append(build_block(tk, split_and_indent(a_raw), b_raw))

# --------------------------------------------------------------------------
# 3) Assemble the final HTML and save it
# --------------------------------------------------------------------------
html = build_html(blocks)

out_dir = Path("data/summaries")
out_dir.mkdir(parents=True, exist_ok=True)

out_file = out_dir / f"InvestmentSummary_{datetime.date.today()}.html"
out_file.write_text(html, encoding="utf-8")

print("✔ saved", out_file)