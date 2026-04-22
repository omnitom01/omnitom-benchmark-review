# OmniToM Code Release

This repository contains the code files accompanying the OmniToM benchmark release. It provides the benchmark dataset together with prompt builders for belief extraction, belief labeling, and semantic-judge evaluation.

![OmniToM two-stage workflow](assets/figure2_omnitom_pipeline.png)

## Included Files

- `benchmark_story_belief_labels.jsonl`
  - Benchmark dataset file.
  - One JSON object per story.
  - Includes story text, story category, and grouped belief annotations with schema labels.
- `benchmark_prompting.py`
  - Utilities for loading benchmark stories and reconstructing belief tables.
- `prompts_extract.py`
  - Extraction prompt builder.
- `prompts_label.py`
  - Labeling prompt builder.
- `prompt_evaluate.py`
  - Semantic-judge prompt builder.
- `assets/figure2_omnitom_pipeline.png`
  - Workflow figure used in this README.

## What This Repo Provides

The files in this repository support three benchmark tasks:

1. load stories and belief annotations from the benchmark dataset
2. build prompts for belief extraction
3. build prompts for belief labeling
4. build prompts for semantic-judge evaluation

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
