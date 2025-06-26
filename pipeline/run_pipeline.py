import datetime
from pathlib import Path
from llm_calls import stage_a, stage_b
from formatter import split_and_indent

TRANSCRIPT = Path("data/transcripts/dinnerTranscript.txt").read_text()

# Run Stage A and B separately
a_raw = stage_a("MEETING", TRANSCRIPT)
b_raw = stage_b("MEETING", TRANSCRIPT)
a_bullets = split_and_indent(a_raw)

# Build HTML
final_html = '''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body { background:#000; color:#fff; font-family:Arial,sans-serif; line-height:1.5; padding:40px; }
  h2.hdr { font-size:22px; font-weight:bold; margin:30px 0 10px; }
  h2.hdr .ticker { font-weight:bold; font-size:24px; color:#ffffff; }
  h2.hdr .rest { font-weight:normal; font-size:20px; color:#ffffff; }
  ul { padding-left: 20px; }
  .lvl1 > li { margin: 10px 0; }
  .lvl2 { list-style-type: circle; }
  .lvl3 { list-style-type: square; }
</style></head><body><section>
'''

final_html += '<h2 class="hdr"><span class="ticker">MEETING</span> <span class="rest">— Summary</span></h2>\n<ul class="lvl1">\n'

for line in a_bullets.strip().splitlines():
    indent = line.count(' ')
    clean = line.strip(' •').strip()
    if indent == 0:
        final_html += f'<li>{clean}</li>\n'
    elif indent == 1:
        final_html += f'<ul class="lvl2"><li>{clean}</li></ul>\n'
    elif indent == 2:
        final_html += f'<ul class="lvl3"><li>{clean}</li></ul>\n'

final_html += '</ul>\n<ul class="lvl1">\n<li>Quick Stats / Metrics<ul class="lvl2">\n'

for line in b_raw.strip().splitlines():
    indent = line.count(' ')
    clean = line.strip(' •').strip()
    if indent == 0:
        final_html += f'<li>{clean}</li>\n'
    elif indent == 1:
        final_html += f'<ul class="lvl2"><li>{clean}</li></ul>\n'
    elif indent == 2:
        final_html += f'<ul class="lvl3"><li>{clean}</li></ul>\n'

final_html += '</ul></li></ul>\n</section></body></html>'

out = Path(f"data/summaries/InvestmentSummary_{datetime.date.today()}.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(final_html, encoding="utf-8")
print("✔ saved", out)
