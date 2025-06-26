import datetime
import re
from pathlib import Path
from llm_calls import stage_a, stage_b
from formatter import split_and_indent, build_block, build_html

# --------------------------------------------------------------------------- #
# 1.  Load and compress transcript
# --------------------------------------------------------------------------- #
TRANSCRIPT_RAW = Path("data/transcripts/dinnerTranscript.txt").read_text()

def compress_transcript(raw_text: str) -> str:
    """Strip speaker/timestamp headers to save tokens (e.g. 'Speaker 4 [00:01:56]' → '4')"""
    lines = raw_text.strip().splitlines()
    compressed = []

    for line in lines:
        match = re.match(r"Speaker\s+(\d+)\s+\[\d{2}:\d{2}:\d{2}\]\s*(.*)", line)
        if match:
            speaker, content = match.groups()
            if content.strip():
                compressed.append(f"{speaker} {content.strip()}")
        elif line.strip():
            compressed.append(line.strip())

    header = (
        "NOTE: Each line begins with a speaker number (e.g. '1'). "
        "Use this to track speaker turns.\n"
    )
    return header + "\n" + "\n".join(compressed)

TRANSCRIPT = compress_transcript(TRANSCRIPT_RAW)

# --------------------------------------------------------------------------- #
# 2.  Run Stage A + Stage B once (full summary)
# --------------------------------------------------------------------------- #
a_raw = stage_a("MEETING", TRANSCRIPT)
b_raw = stage_b("MEETING", TRANSCRIPT)
blocks = [build_block("MEETING", split_and_indent(a_raw), b_raw)]

# --------------------------------------------------------------------------- #
# 3.  Build & save HTML (black background, V9 layout)
# --------------------------------------------------------------------------- #
html = build_html(blocks)
out = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print("✔ saved", out)
