"""
pipeline/run_pipeline.py   ·   V9 prompt-slice runner
====================================================

Flow
----
1. Read MtgGPTPromptV9a.txt  (Stage-A instructions)
2. Read MtgGPTPromptV9b.txt  (Stage-B instructions)
3. Compress transcript lines  Speaker N [hh:mm:ss] → "N|mm text"
4. Call stage_a / stage_b once each
5. Embed Stage B under “Quick Stats / Metrics”
6. Wrap in dark-mode HTML and save to data/summaries/…
"""

from __future__ import annotations
import re, datetime
from pathlib import Path
from llm_calls import stage_a, stage_b    # two-arg versions

# ───────────────────── 1 · Load prompt slices ──────────────────────────────
PROMPT_A = Path("prompts/MtgGPTPromptV9a.txt").read_text()
PROMPT_B = Path("prompts/MtgGPTPromptV9b.txt").read_text()

# ───────────────────── 2 · Compress transcript ─────────────────────────────
raw_lines = Path("data/transcripts/dinnerTranscript.txt").read_text().splitlines()

def compress(lines: list[str]) -> str:
    """
    'Speaker 4 [00:07:12] text' → '4|7 text'
    (minute only; drop hours & seconds)
    """
    patt = re.compile(r"Speaker\s+(\d+)\s+\[\d{2}:(\d{2}):\d{2}]\s+(.*)")
    out  = []
    for ln in lines:
        m = patt.match(ln)
        if m:
            speaker, mm, txt = m.groups()
            out.append(f"{speaker}|{int(mm)} {txt.strip()}")
    header = "NOTE: Each line begins SPEAKER|MINUTE\n\n"
    return header + "\n".join(out)

TRANSCRIPT = compress(raw_lines)

# ───────────────────── 3 · GPT calls ───────────────────────────────────────
print("🔸 Calling Stage A …")
a_text = stage_a(PROMPT_A, TRANSCRIPT)

print("🔸 Calling Stage B …")
b_text = stage_b(PROMPT_B, TRANSCRIPT)

# ───────────────────── 4 · Build final HTML ────────────────────────────────
html_body = f"""
<h2 class='hdr'><span class='ticker'>MEETING</span>
<span class='rest'>— Summary</span></h2>

<pre>{a_text.strip()}</pre>

<ul class="lvl1">
  <li>• <strong>Quick Stats / Metrics</strong>
    <pre>{b_text.strip()}</pre>
  </li>
</ul>
"""

FINAL_HTML = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
 body {{background:#000;color:#fff;font-family:Arial,sans-serif;line-height:1.5;padding:40px}}
 h2.hdr {{font-size:22px;font-weight:bold;margin:30px 0 10px}}
 h2.hdr .ticker {{font-size:24px;font-weight:bold;color:#fff}}
 h2.hdr .rest   {{font-size:20px;font-weight:normal;color:#fff}}
 pre {{white-space:pre-wrap;font-size:16px}}
 ul.lvl1 > li {{margin:10px 0}}
</style></head><body>{html_body}</body></html>"""

# ───────────────────── 5 · Save summary ────────────────────────────────────
out_path = Path(
    f"data/summaries/InvestmentSummary_{datetime.date.today()}.html"
)
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(FINAL_HTML, encoding="utf-8")
print("✔️  Pipeline complete — saved", out_path)
