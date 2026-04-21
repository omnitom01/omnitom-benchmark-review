# OmniToM Code Release

This folder contains the publication-facing code artifacts for the OmniToM benchmark release. The goal is narrow and practical: keep the prompt builders and benchmark JSONL together so the official benchmark can be regenerated, inspected, and evaluated without pulling in the full experiment workspace.

![OmniToM two-stage workflow](assets/figure2_omnitom_pipeline.png)

## Included Files

- `benchmark_story_belief_labels.jsonl`
  - Canonical benchmark release file.
  - One JSON object per story.
  - Includes story text, story category, and grouped belief annotations with schema labels.
- `benchmark_prompting.py`
  - Shared loader/formatter utilities for benchmark story lookup and table reconstruction.
- `prompts_extract.py`
  - Benchmark-facing Stage 1 prompt builder.
  - Uses the released L3 extraction prompt.
- `prompts_label.py`
  - Benchmark-facing Stage 2 prompt builder.
  - Uses the released L3 labeling prompt.
- `prompt_evaluate.py`
  - Benchmark-facing semantic judge prompt builder.
  - Uses the released L4 judge prompt with the first 3 few-shot examples only.
- `assets/figure2_omnitom_pipeline.png`
  - Framework figure for the README.

## What This Repo Does

The code here is deliberately small:

1. Load a story and its official benchmark record from `benchmark_story_belief_labels.jsonl`.
2. Rebuild the exact prompt payloads used for extraction, labeling, and semantic judging.
3. Keep the benchmark-facing prompt logic separate from the larger experiment workspace.

## Quick Usage

```python
from benchmark_prompting import load_story_record
from prompts_extract import build_extract_messages
from prompts_label import build_label_messages
from prompt_evaluate import build_evaluation_messages

record = load_story_record(1)
extract_system, extract_user = build_extract_messages(1)
label_system, label_user = build_label_messages(1)

predictions_csv = 'Actor,Belief\n"world","Example belief"'
judge_system, judge_user = build_evaluation_messages(1, predictions_csv)
```

## Prompt Design Notes

- Stage 1 extraction uses only the published L3 extraction prompt.
- Stage 2 labeling uses only the published L3 labeling prompt.
- The semantic judge uses the published L4 prompt family with only the first 3 few-shot examples.
- The released prompt builders do not depend on the full experiment directories.

## Intentionally Omitted

- experiment outputs
- notebook artifacts
- historical run folders
- analysis plots
- calibration-only or internal working files

## Dataset Card

- `HF_DATASET_CARD.md`
  - Anonymous Hugging Face dataset card draft.

## Local Artifact Note

- `BENCHMARK_README.md`
  - Local artifact note for the JSONL file and statistics.
  - Keep it local unless you want a second, artifact-level README in the public release.

## License

No final redistribution license is embedded here yet. Keep the release metadata consistent with the dataset card until the license is finalized.
