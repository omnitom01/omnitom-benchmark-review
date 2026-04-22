---
pretty_name: OmniToM
language:
- en
license: mit
task_categories:
- text-generation
- text-classification
- question-answering
task_ids:
- information-extraction
- text-classification
size_categories:
- 1K<n<10K
tags:
- theory-of-mind
- benchmark
- social-reasoning
- belief-modeling
- llm-evaluation
- cognitive-reasoning
---

# Dataset Card for OmniToM

## Dataset Details

### Dataset Description

OmniToM is a benchmark for evaluating Theory of Mind in language models through explicit belief-structure modeling. Instead of scoring only endpoint answers to social reasoning questions, OmniToM exposes the intermediate belief structure that a model must build in order to reason coherently about what different actors know, believe, infer, intend, or misunderstand.

Each example is a short story paired with:

- a set of actor-centered belief propositions
- a reserved `world` actor for narrator/world facts
- a seven-dimensional schema label vector for every belief

The benchmark supports two linked tasks:

1. **Belief Extraction**
   - Given a story, extract the relevant belief structure as `(Actor, Belief, Order)` tuples.
2. **Belief Labeling**
   - Given the story and belief tuples, label each belief along seven closed-set schema dimensions.

- **Language(s):** English

### Licensing Information

The upstream ToMBench repository is distributed under the MIT License. OmniToM reuses ToMBench story text and adds new benchmark annotations, prompt builders, release documentation, and replication code. Unless otherwise noted, the OmniToM release package is distributed under the MIT License. Third-party model APIs and hosted services referenced by the public runner are not redistributed.

## Uses

### Direct Use

OmniToM is designed for benchmark evaluation rather than fine-tuning alone. Suitable uses include:

- zero-shot or few-shot belief extraction
- zero-shot or few-shot belief labeling
- semantic-judge evaluation of extracted belief tables
- analysis of multi-actor and higher-order Theory-of-Mind reasoning
- process-sensitive evaluation beyond endpoint question answering

### Out-of-Scope Use

OmniToM should not be treated as:

- a direct measure of real-world social intelligence
- a measure of embodied, interactive, or multimodal social reasoning
- a safety certification benchmark for deployed systems
- a complete coverage benchmark for all possible Theory-of-Mind phenomena

## Dataset Structure

### Data Instances

Each line in the release file is one JSON object:

```json
{
  "story_id": 1,
  "story_category": "Ambiguous Story Task",
  "story": "Story text...",
  "beliefs": [
    {
      "actor": "world",
      "belief": "A minimal propositional statement.",
      "labels": {
        "order": "0",
        "truth_status": "True",
        "knowledge_access": "Public",
        "representation": "Explicit",
        "content_type": "Action/Event",
        "mental_source": "Narration",
        "context": "Neutral"
      }
    }
  ]
}
```

### Data Fields

- `story_id`
  - Unique integer identifier for the story.
- `story_category`
  - One of seven retained benchmark categories.
- `story`
  - Raw story text used for both extraction and labeling tasks.
- `beliefs`
  - List of annotated belief rows.
- `beliefs[].actor`
  - Belief holder. The reserved actor `world` denotes narrator/world facts.
- `beliefs[].belief`
  - Minimal propositional belief statement.
- `beliefs[].labels.order`
  - Recursive depth in `{0,1,2,3}`.
- `beliefs[].labels.truth_status`
  - `True`, `False`, or `Unknown`.
- `beliefs[].labels.knowledge_access`
  - `Private`, `Shared`, or `Public`.
- `beliefs[].labels.representation`
  - `Explicit` or `Implicit`.
- `beliefs[].labels.content_type`
  - One of the closed-set semantic content categories.
- `beliefs[].labels.mental_source`
  - One of the closed-set source categories.
- `beliefs[].labels.context`
  - `Neutral`, `Temporal`, `Deceptive`, or `Counterfactual`.

### Data Splits

This release contains the benchmark split only:

- `benchmark`: `895` stories

A separate 21-story calibration subset is described in the accompanying paper for benchmark construction and judge validation; it is not part of this release artifact.

## Dataset Creation

### Curation Rationale

OmniToM was created to address a limitation in prior Theory-of-Mind benchmarks for language models: most focus on endpoint question answering rather than on whether the model actually constructs a coherent internal belief representation while reading the story.

OmniToM instead evaluates explicit belief-structure modeling. The benchmark is grounded in short stories from ToMBench and organizes reasoning around a unified belief-level schema influenced by the ATOMS view of Theory-of-Mind ability space.

### Source Data

The benchmark sources its stories from ToMBench. From the original source corpus, OmniToM retains seven story categories whose stories provide sufficiently self-contained mental-state evidence for belief extraction from text alone:

- Ambiguous Story Task
- False Belief Task
- Faux-pas Recognition Test
- Hinting Task Test
- Persuasion Story Task
- Scalar Implicature Test
- Strange Story Task

### Annotation Process

The benchmark was built with a human-calibrated, LLM-assisted annotation pipeline:

- `1,383` source stories in the original corpus
- `916` stories retained after source filtering
- `21` stories reserved for calibration
- `895` stories released in the final benchmark

The accompanying paper reports:

- Stage 1 extraction overlap on the calibration subset: `83.72%`
- Stage 2 exact-match labeling agreement on the calibration subset: `92.21%`
- Human-judge agreement for the final semantic judge: `88.86%`

### Who are the source data producers?

The story texts are sourced from ToMBench. The belief structures and schema labels are benchmark annotations produced through the OmniToM human-calibrated annotation pipeline described in the accompanying paper.

### Personal and Sensitive Information

The release consists of short benchmark stories and belief annotations. It is not designed to contain personal user data, private communications, or real-world sensitive records. As with many story-based datasets, names and social roles may appear in the source material, but the benchmark is intended for research evaluation rather than identification or profiling.

## Bias, Risks, and Limitations

OmniToM is story-based, text-only, and sourced from a specific upstream benchmark distribution. It therefore reflects the representational biases, writing conventions, and coverage limitations of its source stories. Names, roles, and social scenarios may also be unevenly distributed across categories.

Additional known limitations:

- the benchmark evaluates story-based Theory of Mind rather than interactive or multimodal social reasoning
- the released labels come from a human-calibrated LLM-assisted pipeline rather than fully manual annotation of every story
- some schema dimensions remain partly interpretive, especially `Knowledge Access` and `Representation`
- Stage 1 extraction evaluation in the paper relies on a validated semantic judge rather than full human adjudication across the full release

### Recommendations

Users should interpret OmniToM as a diagnostic benchmark for explicit belief-structure modeling. Benchmark scores should not be treated as evidence of robust real-world interpersonal reasoning, embodied social competence, or deployment safety.

## Citation

```bibtex
@misc{omnitom2026,
  title={OmniToM: Benchmarking Theory of Mind in LLMs via Explicit Belief Modeling},
  author={Anonymous Authors},
  year={2026},
  note={Anonymous review release}
}
```

## More Information

This anonymous release is intended to support peer review and benchmark inspection. Public release metadata and authorship details may be updated in a later non-anonymous version.
