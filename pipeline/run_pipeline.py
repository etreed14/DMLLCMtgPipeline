# === run_pipeline.py ===
import re
from pathlib import Path
from llm_calls import stage_a, stage_b

# === Load input files ===
PROMPT = Path("prompts/MtgGPTPromptV9.txt").read_text()
TRANSCRIPT_LINES = Path("data/transcripts/dinnerTranscript.txt").read_text().strip().splitlines()

# === Compress transcript to reduce token load ===
def compress_transcript_lines(lines):
    compressed = []
    for line in lines:
        match = re.match(r"Speaker\\s+(\\d+)\\s+\\[(\\d{2}):(\\d{2}):(\\d{2})\\]\\s+(.*)", line)
        if match:
            speaker, hh, mm, ss, content = match.groups()
            minute = str(int(hh))
            compressed.append(f"{speaker}|{minute} {content.strip()}")
        elif line.strip():
            compressed.append(line.strip())
    return compressed

TRANSCRIPT = "NOTE: Each line begins with SPEAKER|MINUTE.\\n" + "\\n".join(compress_transcript_lines(TRANSCRIPT_LINES))

# === Run Stages A & B ===
a_text = stage_a(PROMPT, TRANSCRIPT)
b_text = stage_b(PROMPT, TRANSCRIPT)

# === Save A & B for inspection ===
Path("/mnt/data/StageA.txt").write_text(a_text)
Path("/mnt/data/StageB.txt").write_text(b_text)

# === Simple Stage C logic (inline) ===
def stage_c_concat(stage_a_text: str, stage_b_text: str) -> str:
    return f\"\"\"
<h2 class='hdr'><span class='ticker'>STAGE A</span> <span class='rest'>— Narrative Summary</span></h2>
<pre>{stage_a_text.strip()}</pre>

<h2 class='hdr'><span class='ticker'>STAGE B</span> <span class='rest'>— Fact Ledger</span></h2>
<pre>{stage_b_text.strip()}</pre>
\"\"\"

# === Build HTML output ===
c_html = stage_c_concat(a_text, b_text)

final_html = f\"\"\"<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
  body {{ background:#000; color:#fff; font-family:Arial,sans-serif; line-height:1.5; padding:40px; }}
  h2.hdr {{ font-size:22px; font-weight:bold; margin:30px 0 10px; }}
  h2.hdr .ticker {{ font-weight:bold; font-size:24px; color:#ffffff; }}
  h2.hdr .rest {{ font-weight:normal; font-size:20px; color:#ffffff; }}
  pre {{ white-space:pre-wrap; font-size:16px; }}
</style></head><body>{c_html}</body></html>\"\"\"

Path("/mnt/data/InvestmentSummaryV9.html").write_text(final_html, encoding="utf-8")
print("[Download summary](sandbox:/mnt/data/InvestmentSummaryV9.html?_chatgptios_conversationID=685aef7e-801c-8000-87bc-8b573a5fd0df&_chatgptios_messageID=347ef221-f730-40fb-9a4c-10cf5328ffa3)")
