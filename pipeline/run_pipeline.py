# === run_pipeline.py ===
import re
from pathlib import Path
from llm_calls import stage_a, stage_b
from stage_c_simple import stage_c_concat

# === Load input files ===
PROMPT = Path("prompts/MtgGPTPromptV9.txt").read_text()
TRANSCRIPT_LINES = Path("data/transcripts/dinnerTranscript.txt").read_text().strip().splitlines()

# === Compress transcript to reduce token load ===
def compress_transcript_lines(lines):
    compressed = []
    for line in lines:
        match = re.match(r"Speaker\s+(\d+)\s+\[(\d{2}):(\d{2}):(\d{2})\]\s+(.*)", line)
        if match:
            speaker, hh, mm, ss, content = match.groups()
            minute = str(int(hh))  # collapse to hour bucket
            compressed.append(f"{speaker}|{minute} {content.strip()}")
        elif line.strip():
            compressed.append(line.strip())
    return compressed

TRANSCRIPT = "NOTE: Each line begins with SPEAKER|MINUTE.\n" + "\n".join(compress_transcript_lines(TRANSCRIPT_LINES))

# === Run Stages A & B ===
a_text = stage_a(PROMPT, TRANSCRIPT)
b_text = stage_b(PROMPT, TRANSCRIPT)

# === Save A & B clean for inspection ===
Path("/mnt/data/StageA.txt").write_text(a_text)
Path("/mnt/data/StageB.txt").write_text(b_text)

# === Run Stage C ===
c_html = MtgGPTPromptV9c(a_text, b_text)

# === Wrap in dark mode HTML ===
final_html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
  body {{ background:#000; color:#fff; font-family:Arial,sans-serif; line-height:1.5; padding:40px; }}
  h2.hdr {{ font-size:22px; font-weight:bold; margin:30px 0 10px; }}
  h2.hdr .ticker {{ font-weight:bold; font-size:24px; color:#ffffff; }}
  h2.hdr .rest {{ font-weight:normal; font-size:20px; color:#ffffff; }}
  pre {{ white-space:pre-wrap; font-size:16px; }}
</style></head><body>{c_html}</body></html>"""

Path("/mnt/data/InvestmentSummaryV9.html").write_text(final_html, encoding="utf-8")
print("[Download summary](sandbox:/mnt/data/InvestmentSummaryV9.html?_chatgptios_conversationID=685aef7e-801c-8000-87bc-8b573a5fd0df&_chatgptios_messageID=8c9901bf-79d0-4c84-976d-a3fe8ce08744)")
