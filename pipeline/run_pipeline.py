import re
import datetime
from pathlib import Path
from llm_calls import stage_a, stage_b
from formatter import split_and_indent, build_block, build_html

# === Load prompt & transcript ===
PROMPT = Path("prompts/MtgGPTPromptV9.txt").read_text()
raw_lines = Path("data/transcripts/dinnerTranscript.txt").read_text().strip().splitlines()

# === Compress transcript to reduce token load ===
def compress_transcript_lines(lines):
    compressed = []
    for line in lines:
        match = re.match(r"Speaker\s+(\d+)\s+\[(\d{2}):\d{2}:\d{2}\]\s+(.*)", line)
        if match:
            speaker, minute, content = match.groups()
            minute = str(int(minute))  # strip leading zeroes
            compressed.append(f"{speaker}|{minute} {content.strip()}")
        elif line.strip():
            compressed.append(line.strip())
    return compressed

compressed_lines = compress_transcript_lines(raw_lines)
TRANSCRIPT = (
    "NOTE: Each line begins with SPEAKER|MINUTE. Use this to track turns.\n\n"
    + "\n".join(compressed_lines)
)

# === Run Stage A + B together (one-time full sweep) ===
a_raw = stage_a("MEETING", TRANSCRIPT)
b_raw = stage_b("MEETING", TRANSCRIPT)

# === Merge + format ===
blocks = [build_block("MEETING", split_and_indent(a_raw), b_raw)]
html = build_html(blocks)

# === Output final summary ===
out = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print("✔ saved", out)
