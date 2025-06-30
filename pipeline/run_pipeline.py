"""
run_pipeline.py  ·  V9 prompt-slice runner
==========================================

1. Reads MtgGPTPromptV9a.txt and MtgGPTPromptV9b.txt
2. Compresses 'Speaker n [hh:mm:ss] …' → 'n|mm …'
3. Sends transcript to stage_a / stage_b
4. Concats A + B into dark-mode HTML
5. Saves to data/summaries/InvestmentSummary_<date>.html
"""

import re, datetime
from pathlib import Path
from llm_calls import stage_a, stage_b

# ── 1 · Load prompt slices ───────────────────────────────────────────
PROMPT_A = Path("prompts/MtgGPTPromptV9a.txt").read_text()
PROMPT_B = Path("prompts/MtgGPTPromptV9b.txt").read_text()

# ── 2 · Load & compress transcript ───────────────────────────────────
raw_lines = Path("data/transcripts/dinnerTranscript.txt").read_text().splitlines()

def compress(lines: list[str]) -> str:
    """
    'Speaker 4 [00:07:12] text' → '4|7 text'
    (Keep only minute; drop hours/seconds.)
    """
    out = []
    patt = re.compile(r"Speaker\s+(\d+)\s+\[\d{2}:(\d{2}):\d{2}\]\s+(.*)")
    for ln in lines:
        m = patt.match(ln)
        if m:
            speaker, mm, txt = m.groups()
            out.append(f"{speaker}|{int(mm)} {txt.strip()}")
    header = "NOTE: Each line starts SPEAKER|MIN.\n\n"
    return header + "\n".join(out)

TRANSCRIPT = compress(raw_lines)

# ── 3 · Generate Stage A & B once ────────────────────────────────────
a_text = stage_a(PROMPT_A, TRANSCRIPT)
b_text = stage_b(PROMPT_B, TRANSCRIPT)

# ── 4 · Lightweight Stage C: concat A + B in HTML wrapper ────────────
html_body = (
    "<h2 class='hdr'><span class='ticker'>STAGE A</span> "
    "<span class='rest'>— Narrative Summary</span></h2>\n"
    f"<pre>{a_text.strip()}</pre>\n\n"
    "<h2 class='hdr'><span class='ticker'>STAGE B</span> "
    "<span class='rest'>— Fact Ledger</span></h2>\n"
    f"<pre>{b_text.strip()}</pre>"
)

FINAL_HTML = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
 body {{background:#000;color:#fff;font-family:Arial,sans-serif;line-height:1.5;padding:40px}}
 h2.hdr {{font-size:22px;font-weight:bold;margin:30px 0 10px}}
 h2.hdr .ticker {{font-size:24px;font-weight:bold;color:#fff}}
 h2.hdr .rest   {{font-size:20px;font-weight:normal;color:#fff}}
 pre {{white-space:pre-wrap;font-size:16px}}
</style></head><body>{html_body}</body></html>"""

# ── 5 · Write summary file ───────────────────────────────────────────
out_path = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(FINAL_HTML, encoding="utf-8")
print("✔️  Pipeline complete — saved", out_path)
