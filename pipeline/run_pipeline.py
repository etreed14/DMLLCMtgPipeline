import re
import datetime
from pathlib import Path
from llm_calls import stage_a, stage_b
from formatter import split_and_indent, build_block, build_html

# === Load & compress transcript ===
raw_lines = Path("data/transcripts/dinnerTranscript.txt").read_text().strip().splitlines()

def compress_transcript_lines(lines):
    compressed = []
    last_minute = None
    for line in lines:
        match = re.match(r"Speaker\s+(\d+)\s+\[(\d{2}):(\d{2}):\d{2}\]\s+(.*)", line)
        if not match:
            continue
        speaker, mm, ss, content = match.groups()
        minute = int(mm.lstrip("0") or "0")
        if minute != last_minute:
            last_minute = minute
        prefix = f"{speaker}|{minute}"
        compressed.append(f"{prefix} {content.strip()}")
    return compressed

compressed_lines = compress_transcript_lines(raw_lines)
NOTE = "NOTE: Each line starts with SPEAKER|MINUTE. Use this to track turns.\n"
full_transcript = NOTE + "\n" + "\n".join(compressed_lines)

# === Split by company chunks ===
COMPANIES = [
    "TDC", "Teradata", "AES", "CMG", "Chipotle", "MTCH", "Match", "Hinge",
    "LGF", "Lionsgate", "GOOG", "GOOGL", "Google", "AMZN", "Amazon", "META",
    "FB", "MSFT", "Microsoft", "NVDA", "Nvidia", "SNOW", "Snowflake", "ELF"
]
company_pattern = re.compile(r"\b(" + "|".join(COMPANIES) + r")\b", re.I)

chunks = []
current = []
for line in compressed_lines:
    if company_pattern.search(line) and current:
        chunks.append("\n".join(current))
        current = [line]
    else:
        current.append(line)
if current:
    chunks.append("\n".join(current))

# === Run stage A + B per chunk and assemble ===
blocks = []
for chunk in chunks:
    a = stage_a("MEETING", chunk)
    b = stage_b("MEETING", chunk)
    blocks.append(build_block("MEETING", split_and_indent(a), b))

# === Output final summary ===
html = build_html(blocks)
out = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print("✔ saved", out)
