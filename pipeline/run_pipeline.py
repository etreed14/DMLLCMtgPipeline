# run_pipeline.py  ·  V9 (prompt-slice) runner
# ==========================================================
# • Reads MtgGPTPromptV9a.txt  (Stage A instructions)
# • Reads MtgGPTPromptV9b.txt  (Stage B instructions)
# • Compresses the transcript lines to  "SPEAKER|MIN text"
# • Calls llm_calls.stage_a / stage_b   (two-arg versions)
# • Builds minimal HTML and writes it to data/summaries/…

import re, datetime
from pathlib import Path
from llm_calls import stage_a, stage_b                  # (prompt_part, transcript)

# ── 1)  Load prompt slices ─────────────────────────────────────────────────
PROMPT_A = Path("prompts/MtgGPTPromptV9a.txt").read_text()
PROMPT_B = Path("prompts/MtgGPTPromptV9b.txt").read_text()

# ── 2)  Load & compress transcript ────────────────────────────────────────
raw_lines = Path("data/transcripts/dinnerTranscript.txt").read_text().splitlines()

def compress(lines: list[str]) -> str:
    """
    Convert  'Speaker 4 [00:07:12] blah…'   →   '4|7 blah…'
    (Uses *minute*, not hour.)
    """
    out = []
    patt = re.compile(r"Speaker\s+(\d+)\s+\[\d{2}:(\d{2}):\d{2}\]\s+(.*)")
    for ln in lines:
        m = patt.match(ln)
        if m:
            speaker, mm, text = m.groups()
            minute = str(int(mm))                     # strip leading zeros (07→7)
            out.append(f"{speaker}|{minute} {text.strip()}")
    return "NOTE: Each line starts SPEAKER|MIN.\n\n" + "\n".join(out)

TRANSCRIPT = compress(raw_lines)

# ── 3)  Run Stage A and Stage B once each ─────────────────────────────────
a_text = stage_a(PROMPT_A, TRANSCRIPT)
b_text = stage_b(PROMPT_B, TRANSCRIPT)

# Debug helpers (optional): keep or delete
Path("StageA.txt").write_text(a_text,  encoding="utf-8")
Path("StageB.txt").write_text(b_text,  encoding="utf-8")

# ── 4)  Tiny Stage C – just concatenate A + B inside dark-mode HTML ───────
html_body = f"""<h2 class='hdr'><span class='ticker'>STAGE A</span>
<span class='rest'>— Narrative Summary</span></h2>
<pre>{a_text.strip()}</pre>

<h2 class='hdr'><span class='ticker'>STAGE B</span>
<span class='rest'>— Fact Ledger</span></h2>
<pre>{b_text.strip()}</pre>"""

final_html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
 body {{background:#000;color:#fff;font-family:Arial,sans-serif;line-height:1.5;padding:40px}}
 h2.hdr {{font-size:22px;font-weight:bold;margin:30px 0 10px}}
 h2.hdr .ticker {{font-weight:bold;font-size:24px;color:#fff}}
 h2.hdr .rest   {{font-weight:normal;font-size:20px;color:#fff}}
 pre {{white-space:pre-wrap;font-size:16px}}
</style></head><body>{html_body}</body></html>"""

out_path = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(final_html, encoding="utf-8")
print("✔️  Pipeline complete — saved", out_path)
