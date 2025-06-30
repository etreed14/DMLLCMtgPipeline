"""
run_pipeline.py  ·  FINAL V9 WITH MINUTE LOGIC RESTORED
========================================================

• Loads Stage A + B prompts from txt files
• Compresses transcript lines using SPEAKER|MIN only on first line of each minute
• Sends to llm_calls.stage_a / stage_b
• Prints both to console and saves final HTML to /data/summaries/
"""

import re, datetime
from pathlib import Path
from llm_calls import stage_a, stage_b

# ── 1 · Load prompts ───────────────────────────────────────────────────────
PROMPT_A = Path("prompts/MtgGPTPromptV9a.txt").read_text(encoding="utf-8").strip()
PROMPT_B = Path("prompts/MtgGPTPromptV9b.txt").read_text(encoding="utf-8").strip()

# ── 2 · Load & compress transcript ─────────────────────────────────────────
def compress_transcript(raw_lines: list[str]) -> str:
    """
    Compress: Only show SPEAKER|MINUTE on the first line of each minute.
    Remaining lines just show SPEAKER.
    """
    compressed = []
    last_minute = None
    patt = re.compile(r"Speaker\s+(\d+)\s+\[(\d{2}):(\d{2}):\d{2}\]\s+(.*)")

    for line in raw_lines:
        m = patt.match(line)
        if not m:
            continue
        speaker, mm, ss, text = m.groups()
        minute = int(mm)
        if minute != last_minute:
            compressed.append(f"{speaker}|{minute} {text.strip()}")
            last_minute = minute
        else:
            compressed.append(f"{speaker} {text.strip()}")

    header = "NOTE: First line of each minute has SPEAKER|MINUTE.\n\n"
    return header + "\n".join(compressed)

raw_lines = Path("data/transcripts/dinnerTranscript.txt").read_text(encoding="utf-8").splitlines()
TRANSCRIPT = compress_transcript(raw_lines)

# ── 3 · Run Stage A and Stage B ────────────────────────────────────────────
print("🟡 Running Stage A...")
a_text = stage_a(PROMPT_A, TRANSCRIPT)
print("🟢 Stage A complete\n")

print("🟡 Running Stage B...")
b_text = stage_b(PROMPT_B, TRANSCRIPT)
print("🟢 Stage B complete\n")

# Optional: print to console
print("\n📄 STAGE A — SUMMARY:\n" + a_text + "\n")
print("📊 STAGE B — FACT LEDGER:\n" + b_text + "\n")

# Save raw A/B text
Path("StageA.txt").write_text(a_text, encoding="utf-8")
Path("StageB.txt").write_text(b_text, encoding="utf-8")

# ── 4 · Lightweight Stage C: A + B in HTML ─────────────────────────────────
html_body = f"""
<h2 class='hdr'><span class='ticker'>STAGE A</span> <span class='rest'>— Narrative Summary</span></h2>
<pre>{a_text.strip()}</pre>

<h2 class='hdr'><span class='ticker'>STAGE B</span> <span class='rest'>— Fact Ledger</span></h2>
<pre>{b_text.strip()}</pre>
"""

FINAL_HTML = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
  body {{background:#000; color:#fff; font-family:Arial,sans-serif; line-height:1.5; padding:40px}}
  h2.hdr {{font-size:22px; font-weight:bold; margin:30px 0 10px}}
  h2.hdr .ticker {{font-size:24px; font-weight:bold; color:#fff}}
  h2.hdr .rest   {{font-size:20px; font-weight:normal; color:#fff}}
  pre {{white-space:pre-wrap; font-size:16px}}
</style></head><body>{html_body}</body></html>
"""

# ── 5 · Save HTML to disk ─────────────────────────────────────────────────
out_path = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(FINAL_HTML, encoding="utf-8")
print("✅ Pipeline complete — saved to", out_path)
