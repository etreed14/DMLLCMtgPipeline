# === run_pipeline.py ===
import re
from pathlib import Path
from llm_calls import stage_a, stage_b

print("=== DEBUG PROMPT_A first two lines ===")
print(Path("prompts/MtgGPTPromptV9a.txt").read_text().splitlines()[:2])
print("=== DEBUG PROMPT_B first two lines ===")
print(Path("prompts/MtgGPTPromptV9b.txt").read_text().splitlines()[:2])

# ── 1. Load prompt files ────────────────────────────────────────────────────
PROMPT_A = Path("prompts/MtgGPTPromptV9a.txt").read_text()
PROMPT_B = Path("prompts/MtgGPTPromptV9b.txt").read_text()
PROMPT_C = Path("prompts/MtgGPTPromptV9c.txt").read_text()   # (unused for now)

# ── 2. Load and compress transcript ────────────────────────────────────────
transcript_lines = Path("data/transcripts/dinnerTranscript.txt").read_text().strip().splitlines()

def compress(lines):
    out = []
    patt = re.compile(r"Speaker\s+(\d+)\s+\[(\d{2}):(\d{2}):(\d{2})\]\s+(.*)")
    for ln in lines:
        m = patt.match(ln)
        if m:
            speaker, hh, mm, ss, content = m.groups()
            out.append(f"{speaker}|{int(hh)} {content.strip()}")
        elif ln.strip():
            out.append(ln.strip())
    return out

TRANSCRIPT = "NOTE: Each line begins with SPEAKER|MINUTE.\n" + "\n".join(compress(transcript_lines))

print("—CI sanity check—  first 3 lines of V9a:")
print(Path("prompts/MtgGPTPromptV9a.txt").read_text().splitlines()[:3])

print("—CI sanity check—  first 2 lines of V9b:")
print(Path("prompts/MtgGPTPromptV9b.txt").read_text().splitlines()[:2])

# ── 3. Run Stage A and B exactly once each ─────────────────────────────────
a_text = stage_a(PROMPT_A, TRANSCRIPT)
b_text = stage_b(PROMPT_B, TRANSCRIPT)

Path("StageA.txt").write_text(a_text)
Path("StageB.txt").write_text(b_text)

# ── 4. Minimal Stage C: just concatenate A + B ─────────────────────────────
def stage_c_concat(a: str, b: str) -> str:
    return f"""
<h2 class='hdr'><span class='ticker'>STAGE A</span> <span class='rest'>— Narrative Summary</span></h2>
<pre>{a.strip()}</pre>

<h2 class='hdr'><span class='ticker'>STAGE B</span> <span class='rest'>— Fact Ledger</span></h2>
<pre>{b.strip()}</pre>
"""

c_html = stage_c_concat(a_text, b_text)

# ── 5. Wrap in dark-mode HTML and write output ─────────────────────────────
final_html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
 body {{background:#000;color:#fff;font-family:Arial,sans-serif;line-height:1.5;padding:40px}}
 h2.hdr {{font-size:22px;font-weight:bold;margin:30px 0 10px}}
 h2.hdr .ticker {{font-weight:bold;font-size:24px;color:#fff}}
 h2.hdr .rest {{font-weight:normal;font-size:20px;color:#fff}}
 pre {{white-space:pre-wrap;font-size:16px}}
</style></head><body>{c_html}</body></html>"""

Path("InvestmentSummaryV9.html").write_text(final_html, encoding="utf-8")
print("✔️  Pipeline complete — output saved to InvestmentSummaryV9.html")
