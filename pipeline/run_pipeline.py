"""
Generate an HTML meeting summary (V9 logic, single-pass).

• Stage A  – Narrative summary
• Stage B  – Bullet ledger
• Stage C  – HTML assembly               (done here)
"""

import datetime
from pathlib import Path

from llm_calls import stage_a, stage_b
from formatter  import split_and_indent, build_block, build_html

# --------------------------------------------------------------------------- #
# 1.  Load prompt & transcript
# --------------------------------------------------------------------------- #
BASE_PROMPT = Path("prompts/MtgGPTPromptV9.txt").read_text()
TRANSCRIPT  = Path("data/transcripts/dinnerTranscript.txt").read_text()

# --------------------------------------------------------------------------- #
# 2.  Produce Stage A and Stage B once (no ticker filtering)
# --------------------------------------------------------------------------- #
a_raw = stage_a("MEETING", BASE_PROMPT, TRANSCRIPT)
b_raw = stage_b("MEETING", BASE_PROMPT, TRANSCRIPT)

blocks = [build_block("MEETING", split_and_indent(a_raw), b_raw)]

# --------------------------------------------------------------------------- #
# 3.  Build & save HTML
# --------------------------------------------------------------------------- #
html = build_html(blocks)
out  = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print("✔  saved", out)
