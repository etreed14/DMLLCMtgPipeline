"""
run_pipeline.py  ·  FINAL V9 WITH MINUTE LOGIC RESTORED
========================================================

• Loads Stage A + B prompts from txt files
• Compresses transcript lines using SPEAKER|MIN only on first line of each minute
• Sends to llm_calls.stage_a / stage_b
• Prints both to console and saves final HTML to /data/summaries/
"""

import re, datetime, sys
from pathlib import Path
from llm_calls import stage_a, stage_b, stage_c

# ── 1 · Load prompts ───────────────────────────────────────────────────────
PROMPT_A = Path("prompts/MtgGPTPromptV9a.txt").read_text(encoding="utf-8").strip()
PROMPT_B = Path("prompts/MtgGPTPromptV9b.txt").read_text(encoding="utf-8").strip()
PROMPT_C = Path("prompts/MtgGPTPromptV9c.txt").read_text(encoding="utf-8").strip()

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

transcript_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/transcripts/dinnerTranscript.txt")
raw_lines = transcript_path.read_text(encoding="utf-8").splitlines()
TRANSCRIPT = compress_transcript(raw_lines)

# ── 3 · Run Stage A and Stage B ────────────────────────────────────────────
print("🟡 Running Stage A...")
a_text = stage_a(PROMPT_A, TRANSCRIPT)
print("🟢 Stage A complete\n")
input("=== END STAGE A (type 'y' to continue) === ")

print("🟡 Running Stage B...")
b_text = stage_b(PROMPT_B, TRANSCRIPT)
print("🟢 Stage B complete\n")
input("=== END STAGE B (type 'y' to append stats) === ")

# Optional: print to console
print("\n📄 STAGE A — SUMMARY:\n" + a_text + "\n")
print("📊 STAGE B — FACT LEDGER:\n" + b_text + "\n")

# Save raw A/B text
Path("StageA.txt").write_text(a_text, encoding="utf-8")
Path("StageB.txt").write_text(b_text, encoding="utf-8")

# ── 4 · Run Stage C ─────────────────────────────────────────────────────-
print("🟡 Running Stage C...")
c_html = stage_c(PROMPT_C, a_text, b_text)
print("🟢 Stage C complete\n")
input("=== END STAGE C (type 'y' to finalize and display) === ")

# ── 5 · Save HTML to disk ─────────────────────────────────────────────────
out_path = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(c_html, encoding="utf-8")
print("✅ Pipeline complete — saved to", out_path)
