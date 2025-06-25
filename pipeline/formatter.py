import html, re

def split_and_indent(a: str) -> str:
    out=[]
    for ln in a.splitlines():
        if " ; " in ln or " and " in ln or " but " in ln:
            first, rest = re.split(r"\s*(?:;| and | but )\s*", ln, 1)
            out.append(first)
            out.append("    • " + rest)
        else:
            out.append(ln)
    return "\n".join(out)

def build_block(ticker: str, cleaned_a: str, raw_b: str) -> str:
    indented_b = "    " + raw_b.replace("\n", "\n    ")
    return (
        f"<h2 class='hdr'><span class='ticker'>{ticker}</span> "
        f"<span class='rest'>— Summary</span></h2>\n"
        f"<pre>{html.escape(cleaned_a)}</pre>\n"
        f"<pre>• Quick Stats / Metrics\n{html.escape(indented_b)}</pre>\n"
    )

def build_html(body_parts: list[str]) -> str:
    css = (
        "body{background:#000;color:#fff;font-family:Arial,sans-serif;line-height:1.5;padding:40px;}"
        "h2.hdr{font-size:22px;font-weight:bold;margin:30px 0 10px;}"
        "h2.hdr .ticker{font-size:24px;font-weight:bold;color:#ffffff;}"
        "h2.hdr .rest{font-size:20px;color:#ffffff;}"
        "ul{padding-left:20px;}"
        ".lvl1>li{margin:10px 0;}"
        ".lvl2{list-style-type:circle;}"
        ".lvl3{list-style-type:square;}"
    )
    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>"
        + "\n".join(body_parts)
        + "</body></html>"
    )
