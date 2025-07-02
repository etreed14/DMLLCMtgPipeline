Meeting Summary Pipeline (V9)
============================

This project processes a meeting transcript through three GPT stages to
generate a final HTML summary. Each stage uses a separate prompt file so
you can update the prompts without touching the code.

### Usage

1. Set your `OPENAI_API_KEY` environment variable.
2. Put the transcript in `data/transcripts/`.
3. Run the pipeline with the transcript path:

```bash
python -m mtg_pipeline.run_pipeline data/transcripts/myTranscript.txt
```

The script loads the current versions of `MtgGPTPromptV9a/b/c.txt` one by one
and pauses after each stage. Type `y` to continue when prompted. The final HTML
output is written to `data/summaries/`.
