import datetime
from pathlib import Path
from collections import defaultdict
from utils import extract_tickers
from llm_calls import stage_a, stage_b
from formatter import split_and_indent, build_block, build_html

OUTDIR = Path("data/summaries")
OUTDIR.mkdir(parents=True, exist_ok=True)

BASE_PROMPT = Path("prompts/MtgGPTPromptV9.txt").read_text()
TRANSCRIPT  = Path("data/transcripts/dinnerTranscript.txt").read_text()

blocks = []
results = {}
propagate_to = defaultdict(list)

tickers = extract_tickers(TRANSCRIPT)
for tk in tickers:
    a_raw = stage_a(tk, BASE_PROMPT, TRANSCRIPT)
    print(f"[{datetime.datetime.now().isoformat()}]  finished Stage A for {tk}", flush=True)
    b_raw = stage_b(tk, BASE_PROMPT, TRANSCRIPT)
    print(f"[{datetime.datetime.now().isoformat()}]  finished Stage B for {tk}", flush=True)
    results[tk] = (a_raw, b_raw)
    for line in (a_raw.splitlines() + b_raw.splitlines()):
        for other in tickers:
            if other != tk and other in line:
                propagate_to[other].append(line)

for tk in tickers:
    a_raw, b_raw = results[tk]
    if propagate_to[tk]:
        cross = '\n'.join('    ' + ln.strip() for ln in propagate_to[tk])
        b_raw += '\n• Cross-referenced points from other discussions\n' + cross
    blocks.append(build_block(tk, split_and_indent(a_raw), b_raw))

html = build_html(blocks)
out = OUTDIR / f"InvestmentSummary_{datetime.date.today()}.html"
out.write_text(html, encoding="utf-8")
print(f"\u2713 saved {out}")
