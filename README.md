Meeting Summary Pipeline (V9)
============================

This project processes a raw meeting transcript through three GPT stages to
produce a final HTML summary.

### Usage

1. Set your `OPENAI_API_KEY` environment variable.
2. Place the transcript file in `data/transcripts/`.
3. Run the pipeline and pass the path to the transcript:

```bash
python pipeline/run_pipeline.py data/transcripts/myTranscript.txt
```

The script pauses after each stage. Type `y` to continue to the next step. The
final HTML is saved to `data/summaries/`.
