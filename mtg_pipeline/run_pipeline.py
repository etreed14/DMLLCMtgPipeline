from pathlib import Path
import sys
from .stages import run_stage

PROMPTS_DIR = Path('prompts')

def read_transcript(path: Path) -> str:
    return path.read_text(encoding='utf-8')

def compress(lines: list[str]) -> str:
    out = []
    last_min = None
    for ln in lines:
        if not ln.strip():
            continue
        parts = ln.split(maxsplit=3)
        if len(parts) < 4:
            continue
        speaker, timecode, _, text = parts
        mm = timecode[1:3]
        minute = int(mm)
        if minute != last_min:
            out.append(f"{speaker}|{minute} {text.strip()}")
            last_min = minute
        else:
            out.append(f"{speaker} {text.strip()}")
    header = "NOTE: First line of each minute has SPEAKER|MINUTE.\n\n"
    return header + "\n".join(out)

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m mtg_pipeline.run_pipeline <transcript.txt>")
        sys.exit(1)

    t_path = Path(sys.argv[1])
    raw_lines = t_path.read_text(encoding='utf-8').splitlines()
    transcript = compress(raw_lines)

    print('🟡 Running Stage A…')
    a_text = run_stage(PROMPTS_DIR / 'MtgGPTPromptV9a.txt', transcript)
    print('🟢 Stage A complete\n')
    input("=== END STAGE A (type 'y' to continue) === ")

    print('🟡 Running Stage B…')
    b_text = run_stage(PROMPTS_DIR / 'MtgGPTPromptV9b.txt', transcript)
    print('🟢 Stage B complete\n')
    input("=== END STAGE B (type 'y' to append stats) === ")

    print('\n📄 STAGE A — SUMMARY:\n' + a_text + '\n')
    print('📊 STAGE B — FACT LEDGER:\n' + b_text + '\n')

    print('🟡 Running Stage C…')
    user = f"STAGE_A:\n{a_text.strip()}\n\nSTAGE_B:\n{b_text.strip()}"
    c_html = run_stage(PROMPTS_DIR / 'MtgGPTPromptV9c.txt', user)
    print('🟢 Stage C complete\n')
    input("=== END STAGE C (type 'y' to finalize) === ")

    out_path = Path('data/summaries') / f'Summary_{t_path.stem}.html'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(c_html, encoding='utf-8')
    print('✅ Pipeline complete — saved to', out_path)

if __name__ == '__main__':
    main()
