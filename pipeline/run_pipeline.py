import datetime
from pathlib import Path
from utils import extract_tickers
from llm_calls import stage_a, stage_b
from formatter import split_and_indent, build_block, build_html

BASE_PROMPT = Path("prompts/MtgGPTPromptV9.txt").read_text()
TRANSCRIPT  = Path("data/transcripts/dinnerTranscript.txt").read_text()

blocks = []
for tk in extract_tickers(TRANSCRIPT):
    a_raw = stage_a(tk, BASE_PROMPT, TRANSCRIPT)
    b_raw = stage_b(tk, BASE_PROMPT, TRANSCRIPT)
    blocks.append(build_block(tk, split_and_indent(a_raw), b_raw))

html = build_html(blocks)
out  = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print("✔ saved", out)