"""
run_pipeline.py  –  V9 (3-file prompt) runner

• Compresses transcript to "SPEAKER|MIN" format
• Runs Stage A and Stage B once on the full transcript
• Builds dark-mode HTML summary
"""

import re, datetime
from pathlib import Path
from llm_calls import stage_a, stage_b      # now (prompt_part, transcript)
from formatter import split_and_indent, build_block, build_html

# ─────────────────────────── 1) Load prompt slices ──────────────────────────
PROMPT_A = Path("prompts/MtgGPTPromptV9a.txt").read_text()
PROMPT_B = Path("prompts/MtgGPTPromptV9b.txt").read_text()

# ─────────────────────────── 2) Load & compress transcript ──────────────────
RAW_LINES = Path("data/transcripts/dinnerTranscript.txt").read_text().splitlines()

def compress(lines: list[str]) -> str:
    out = []
    for ln in lines:
        m = re.match(r"Speaker\s+(\d+)\s+\[(\d{2}):\d{2}:\d{2}\]\s+(.*)", ln)
        if m:
            speaker, mm, text = m.groups()
            minute = str(int(mm))            # strip leading zeros
            out.append(f"{speaker}|{minute} {text.strip()}")
    return "NOTE: Each line starts SPEAKER|MIN.\n\n" + "\n".join(out)

TRANSCRIPT = compress(RAW_LINES)

# ─────────────────────────── 3) Run Stage A & B ─────────────────────────────
a_raw = stage_a(PROMPT_A, TRANSCRIPT)
b_raw = stage_b(PROMPT_B, TRANSCRIPT)

# ─────────────────────────── 4) Build HTML block ────────────────────────────
blocks = [build_block("MEETING", split_and_indent(a_raw), b_raw)]
html   = build_html(blocks)

# ─────────────────────────── 5) Save summary ────────────────────────────────
out = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print("✔  saved", out)
