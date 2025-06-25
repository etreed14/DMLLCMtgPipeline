"""
pipeline/run_pipeline.py
• Runs Stage A ➜ Stage B ➜ Stage C ONCE for the whole transcript
  (no per-ticker filtering).
• Saves V9-style HTML to data/summaries/InvestmentSummary_<date>.html
"""

import datetime
from pathlib import Path
from llm_calls import stage_a, stage_b      # helper wrappers already restored
from formatter import split_and_indent, build_block, build_html

# ----------------------------------------------------------------------
# 1. Load prompt and the *first* .txt file in data/transcripts/
# ----------------------------------------------------------------------
BASE_PROMPT = Path("prompts/MtgGPTPromptV9.txt").read_text()

transcripts = sorted(Path("data/transcripts").glob("*.txt"))
if not transcripts:
    raise SystemExit("🚫  No transcript found in data/transcripts/")

transcript_text = transcripts[0].read_text()
print(f"🟢  Using transcript: {transcripts[0].name}")

# ----------------------------------------------------------------------
# 2. Generate Stage A and Stage B once (ticker = 'ALL')
# ----------------------------------------------------------------------
print("🧠  Generating Stage A …")
a_raw = stage_a("ALL", BASE_PROMPT, transcript_text)

print("🧠  Generating Stage B …")
b_raw = stage_b("ALL", BASE_PROMPT, transcript_text)

# ----------------------------------------------------------------------
# 3. Build HTML (Stage C formatting)
# ----------------------------------------------------------------------
block = build_block("ALL", split_and_indent(a_raw), b_raw)
html  = build_html([block])

# ----------------------------------------------------------------------
# 4. Write file
# ----------------------------------------------------------------------
out_dir = Path("data/summaries")
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / f"InvestmentSummary_{datetime.date.today()}.html"
out_path.write_text(html, encoding="utf-8")
print("✔  saved", out_path)