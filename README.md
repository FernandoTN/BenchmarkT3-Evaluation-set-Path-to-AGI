# T3 Benchmark Expansion Project

**Stanford CS372: Artificial General Intelligence for Reasoning, Planning, and Decision Making**
**Winter 2026 - Group I1**

A comprehensive benchmark dataset expansion system for AI safety evaluation, implementing Pearl's Ladder of Causation and the CRIT (Causal Reasoning Integrity Test) scoring framework.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Final Results](#final-results)
3. [Theoretical Framework](#theoretical-framework)
4. [Architecture](#architecture)
5. [Project Structure](#project-structure)
6. [Installation & Setup](#installation--setup)
7. [Usage](#usage)
8. [Pipeline Components](#pipeline-components)
9. [Case Schema](#case-schema)
10. [Validation System](#validation-system)
11. [Quality Metrics](#quality-metrics)
12. [Deliverables](#deliverables)
13. [References](#references)

---

## Project Overview

This project expands the T3 Benchmark dataset from **49 original cases to 454 validated cases** for evaluating AI systems' causal reasoning capabilities. The benchmark focuses on identifying and testing "reasoning traps" - common fallacies in causal inference that AI systems must learn to recognize and avoid.

### Assignment Context

| Attribute | Value |
|-----------|-------|
| Course | CS372 - Winter 2026 |
| Domain | AI & Technology (D8) |
| Signature Trap | Goodhart's Law |
| Focus | Association (L1), Intervention (L2), Counterfactual (L3) |
| Original Cases | 49 |
| Target Cases | 454 |
| Due Date | January 14, 2026 |
| Status | ✅ **COMPLETED** (January 9, 2026) |

---

## Final Results

### Summary Metrics

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Total Cases | 454 | 454 | ✅ |
| Unique Case IDs | 100% | 100% | ✅ |
| Mean CRIT Score | ≥7.0 | 8.54 | ✅ |
| DAG Validity Rate | ≥95% | 96.9% | ✅ |
| Duplicate Rate | 0% | 0% | ✅ |

### Pearl's Ladder Distribution

| Level | Description | Count | Percentage | Target |
|-------|-------------|-------|------------|--------|
| L1 | Association (Seeing) | 52 | 11.5% | 10-12% |
| L2 | Intervention (Doing) | 277 | 61.0% | 66-70% |
| L3 | Counterfactual (Imagining) | 125 | 27.5% | 18-21% |

### Trap Type Distribution

| Trap Type | Count | Percentage | Description |
|-----------|-------|------------|-------------|
| GOODHART | 93 | 20.5% | Proxy gaming, specification gaming |
| COUNTERFACTUAL | 91 | 20.0% | Wishful thinking, defense efficacy |
| SELECTION_SPURIOUS | 47 | 10.4% | Selection bias, data leakage |
| SPECIFICATION | 42 | 9.3% | Literal interpretation, sim-to-real |
| CONF_MED | 40 | 8.8% | Confounding, mediation errors |
| INSTRUMENTAL | 39 | 8.6% | Convergent goals, self-preservation |
| FEEDBACK | 30 | 6.6% | Self-fulfilling predictions |
| CALIBRATION | 9 | 2.0% | Confidence calibration |
| TRADE_OFF | 8 | 1.8% | Multi-objective conflicts |
| OTHER | 55 | 12.1% | Alignment, mechanism, etc. |

### Difficulty Distribution

| Difficulty | Count | Percentage |
|------------|-------|------------|
| Easy | 90 | 19.8% |
| Medium | 199 | 43.8% |
| Hard | 165 | 36.3% |

---

## Theoretical Framework

### Pearl's Ladder of Causation

The T3 Benchmark uses Pearl's three-level causal hierarchy to classify reasoning tasks:

#### Level 1: Association (Seeing)
- **Query Type**: P(Y|X) - "What if I see X?"
- **Cognitive Task**: Predict Y given observed X
- **Common Trap**: Confusing correlation with causation
- **Data Required**: Observational data only

```
Example Structure:
Z (deployment scale)
↙    ↘
X      Y
(capabilities) ↔ (safety incidents)
Spurious correlation, not causation
```

#### Level 2: Intervention (Doing)
- **Query Type**: P(Y|do(X)) - "What if I do X?"
- **Cognitive Task**: Predict effect of intervention
- **Common Trap**: Failing to identify backdoor paths
- **Data Required**: Experimental data OR observational + causal structure

```
Example Structure:
X (interpretability) → Y (fewer failures)
Z (team quality) → X
Z (team quality) → Y
Backdoor Path: X ← Z → Y
```

#### Level 3: Counterfactual (Imagining)
- **Query Type**: P(Y_x|X',Y') - "What if X had been different?"
- **Cognitive Task**: Reason about alternative outcomes in specific cases
- **Common Trap**: Wishful thinking, defense efficacy fallacy
- **Data Required**: Full Structural Causal Model (SCM)

```
Three-Step Algorithm:
1. Abduction: Infer U from observations
2. Action: Intervene to set X=x
3. Prediction: Compute counterfactual Y_x
```

### CRIT Scoring Framework

The CRIT (Causal Reasoning Integrity Test) evaluates cases on five dimensions:

| Dimension | Poor (1-2) | Good (5-6) | Exceptional (9-10) |
|-----------|------------|------------|---------------------|
| Scenario Clarity | Vague | Clear with minor gaps | Publication-ready |
| Variable Definition | Missing | All defined | Precise formal notation |
| Trap Mechanism | Invalid | Non-trivial | Novel, deeply instructive |
| Reasoning Chain | Illogical | Complete | Formally valid |
| Wise Refusal | Wrong | Correct | Deep understanding |

**Acceptance Thresholds**:
- Mean CRIT score ≥ 7.0: **PASS**
- Min CRIT score ≥ 5.0: Revise if below
- Structure pass rate ≥ 95%

---

## Architecture

### Master Orchestrator Pattern

The system uses a master orchestrator architecture coordinating 8 specialized generators and 3 validators:

```
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │   (Main Loop)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Generation  │   │  Validation   │   │   Revision    │
│     Phase     │   │     Phase     │   │     Phase     │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
   ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
   │8 Gens   │         │3 Valids │         │Max 3    │
   │(Parallel)│         │(Series) │         │Cycles   │
   └─────────┘         └─────────┘         └─────────┘
```

### Pipeline Phases

1. **Generation Phase**: 8 parallel generators produce cases by trap type
2. **Validation Phase**: DAG, Content, and Cross validators check quality
3. **Revision Phase**: Up to 3 cycles to fix failing cases
4. **Finalization Phase**: Merge with original cases, deduplicate, output

### Implementation Strategy

The final implementation used a **hybrid approach**:

| Phase | Description | Result |
|-------|-------------|--------|
| Phase 1 | Bug fixes (duplicate IDs, schema errors, placeholder detection) | Infrastructure ready |
| Phase 2-3 | Automated pipeline with 0.75 similarity threshold | 281 cases |
| Phase 4 | Agent-based gap filling (173 additional cases) | 454 cases |
| Phase 5 | Final validation and dataset assembly | 100% verified |

---

## Project Structure

```
AGI/
├── README.md                           # This file
├── TODO.md                             # Task tracking
├── docs/
│   ├── course/
│   │   ├── assignments/                # CS372_Win2026_Assignment1.md
│   │   ├── lectures/                   # CS3722026-Lecture2.md
│   │   └── readings/                   # chapter6and7.md (SocraSynth/CRIT)
│   ├── data/
│   │   └── BenchmarkT3-BucketLarge-I.md  # Original 49 cases
│   └── plans/
│       ├── CURRENT_PLAN.md             # Active plan pointer
│       ├── 2026-01-09-complete-454-cases-hybrid.md
│       └── archivedPlans/              # Previous iteration plans
├── project/
│   ├── orchestrator/
│   │   ├── orchestrator.py             # Main pipeline coordinator (1870 lines)
│   │   ├── config.json                 # Target distributions, thresholds
│   │   └── progress_tracker.json       # Real-time progress state
│   ├── generators/
│   │   ├── base_generator.py           # Abstract base class, CRIT integration
│   │   ├── gen_01_goodhart.py          # Goodhart's Law cases
│   │   ├── gen_02_counterfactual.py    # Counterfactual reasoning cases
│   │   ├── gen_03_conf_med.py          # Confounding/Mediation cases
│   │   ├── gen_04_instrumental.py      # Instrumental convergence cases
│   │   ├── gen_05_selection_spurious.py # Selection bias cases
│   │   ├── gen_06_specification.py     # Specification gaming cases
│   │   ├── gen_07_feedback_loops.py    # Feedback loop cases
│   │   └── gen_08_other_traps.py       # Other trap types
│   ├── validators/
│   │   ├── dag_validator.py            # Causal DAG structure validation
│   │   ├── content_validator.py        # CRIT rubric scoring
│   │   └── cross_validator.py          # Duplicate/similarity detection
│   ├── instructions/
│   │   ├── MASTER_INSTRUCTIONS.md      # Generation guidelines
│   │   ├── PEARL_LEVELS.md             # L1/L2/L3 specifications
│   │   ├── TRAP_TYPES.md               # 20+ trap type taxonomy
│   │   ├── CASE_TEMPLATE.md            # JSON case structure
│   │   └── CAUSAL_STRUCTURES.md        # DAG patterns
│   ├── schemas/
│   │   └── case_schema.json            # JSON Schema validation
│   ├── categories/
│   │   ├── original_cases.json         # Parsed original 49 cases
│   │   ├── goodhart/original.json
│   │   ├── counterfactual/original.json
│   │   ├── conf_med/original.json
│   │   ├── instrumental/original.json
│   │   ├── selection_spurious/original.json
│   │   ├── specification/original.json
│   │   ├── feedback_loops/original.json
│   │   └── other_traps/original.json
│   └── output/
│       ├── final/
│       │   └── GroupI1_dataset.json    # FINAL: 454 validated cases
│       ├── generated/                  # Batch outputs by generator
│       ├── validated/                  # Post-validation cases
│       ├── revision/                   # Failed cases after max cycles
│       ├── agent_cases_*.json          # Agent-generated gap fills
│       ├── analysis_report.md          # Methodology documentation
│       └── checkpoint.json             # Crash recovery state
└── scripts/
    └── pdf_to_markdown.py              # Original benchmark parser
```

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- No external dependencies (uses standard library only)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/FernandoTN/BenchmarkT3-Evaluation-set-Path-to-AGI.git
cd AGI

# Verify the final dataset
python3 -c "
import json
d = json.load(open('project/output/final/GroupI1_dataset.json'))
print(f'Total: {len(d)} cases')
ids = [c['case_id'] for c in d]
print(f'Unique IDs: {len(set(ids))}/{len(ids)}')
"
```

---

## Usage

### View Final Dataset Statistics

```bash
# Count cases
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); print(f'Total: {len(d)} cases')"

# Check Pearl level distribution
python3 -c "
import json
from collections import Counter
d = json.load(open('project/output/final/GroupI1_dataset.json'))
levels = Counter(c['annotations']['pearl_level'] for c in d)
print(levels)
"

# Check trap type distribution
python3 -c "
import json
from collections import Counter
d = json.load(open('project/output/final/GroupI1_dataset.json'))
traps = Counter(c['annotations']['trap_type'] for c in d)
for trap, count in traps.most_common():
    print(f'{trap}: {count}')
"
```

### Run the Orchestrator Pipeline

```bash
cd project/orchestrator

# Run full pipeline (generation + validation + revision + finalization)
python orchestrator.py --phase all

# Run individual phases
python orchestrator.py --phase generate    # Generation only
python orchestrator.py --phase validate    # Validation only
python orchestrator.py --phase revise      # Revision only
python orchestrator.py --phase finalize    # Finalization only
python orchestrator.py --phase report      # Generate report only

# With options
python orchestrator.py --phase all --verbose    # Debug logging
python orchestrator.py --phase all --dry-run    # Show what would be done
python orchestrator.py --config /path/to/config.json --phase all
```

---

## Pipeline Components

### Orchestrator (`orchestrator.py`)

The main coordinator implementing:

- **AtomicIDCounter**: Thread-safe unique ID generation
- **PipelinePhase**: SETUP → GENERATION → VALIDATION → REVISION → FINALIZATION → COMPLETE
- **PhaseStatus**: PENDING, IN_PROGRESS, COMPLETED, FAILED
- **IssueSeverity**: CRITICAL, HIGH, MEDIUM, LOW

Key methods:
```python
orchestrator.run_full_pipeline()      # Complete pipeline
orchestrator.run_generation_phase()   # Distribute to 8 generators
orchestrator.run_validation_phase()   # DAG + Content + Cross validation
orchestrator.run_revision_phase()     # Max 3 cycles per case
orchestrator.finalize_dataset()       # Merge, dedupe, output
orchestrator.generate_report()        # Analysis report
```

### Generators (`generators/`)

Each generator extends `BaseGenerator` and implements:

```python
class BaseGenerator(ABC):
    def generate_batch(self, count: int, trap_type: str, subdomains: List[str]) -> List[CaseData]
    def _create_case_template(self, case_num: int, trap_type: str) -> CaseData
    def _assign_pearl_level(self, trap_type: str) -> str
    def _calculate_crit_score(self, case: CaseData) -> float
    def evaluate_case(self, case: CaseData) -> CRITResult
```

Generator allocations from `config.json`:

| Generator | Trap Type | Allocation | Subdomains |
|-----------|-----------|------------|------------|
| gen_01_goodhart | GOODHART | 82 | Scaling, RLHF, Reward Hacking, Game Playing, Legal AI |
| gen_02_counterfactual | COUNTERFACTUAL | 82 | Alignment, Philosophy, Safety, Governance, AGI Theory |
| gen_03_conf_med | CONF_MED | 36 | Medical AI, Fairness, Security, Algorithmic Fairness |
| gen_04_instrumental | INSTRUMENTAL | 37 | Multi-Agent, Corrigibility, Existential Risk |
| gen_05_selection_spurious | SELECTION_SPURIOUS | 43 | CV, NLP, Recommenders, ML Evaluation |
| gen_06_specification | SPECIFICATION | 37 | Autonomous Vehicles, Game Playing, Robustness |
| gen_07_feedback_loops | FEEDBACK | 28 | Educational AI, Social Systems, Criminal Justice AI |
| gen_08_other_traps | OTHER | 60 | Model Compression, Prompt Engineering, Language Models |

### Validators (`validators/`)

#### DAG Validator (`dag_validator.py`)

Validates causal DAG structures with four rules:

| Rule | Severity | Description |
|------|----------|-------------|
| DAG-01 | CRITICAL | Acyclicity check (no cycles allowed) |
| DAG-02 | HIGH | Backdoor criterion validation |
| DAG-03 | HIGH | Collider conditioning warnings |
| DAG-04 | MEDIUM | Variable role consistency |

```python
validator = DAGValidator()
results = validator.validate(case)  # Returns List[ValidationResult]
batch_results = validator.validate_batch(cases)  # Aggregate statistics
```

#### Content Validator (`content_validator.py`)

CRIT rubric scoring on five dimensions:

```python
validator = ContentValidator()
result = validator.validate(case)  # Returns ContentValidationResult
# result.total_score: float (0-10)
# result.dimension_scores: Dict[str, int]
# result.passes_threshold: bool (score >= 7.0)
```

#### Cross Validator (`cross_validator.py`)

Duplicate detection and distribution verification:

```python
validator = CrossValidator(config_path)
result = validator.validate(cases)  # Returns CrossValidationResult
# result.duplicate_count: int
# result.duplicates: List[Tuple[case_id, case_id, similarity]]
# result.pearl_distribution: Dict
# result.trap_distribution: Dict
```

Features:
- Exact duplicate detection (normalized text comparison)
- Semantic similarity (60% SequenceMatcher + 40% n-gram overlap)
- Configurable similarity threshold (default 0.75)
- Placeholder case detection

---

## Case Schema

Each case follows this JSON structure:

```json
{
  "case_id": "8.123",
  "scenario": "Description of the AI safety scenario (10-500 chars)",
  "variables": {
    "X": {"name": "Treatment Variable", "role": "treatment"},
    "Y": {"name": "Outcome Variable", "role": "outcome"},
    "Z": {"name": "Confounder Variable", "role": "confounder"}
  },
  "annotations": {
    "pearl_level": "L2",
    "domain": "D8",
    "trap_type": "GOODHART",
    "trap_subtype": "Proxy Gaming",
    "difficulty": "Medium",
    "subdomain": "RLHF",
    "causal_structure": "X -> Y <- Z, Z -> X",
    "key_insight": "Optimizing a proxy can diverge from the true goal"
  },
  "hidden_structure": "Required for L2 - explains causal mechanism",
  "ground_truth": {
    "verdict": "CONDITIONAL",
    "justification": "Required for L3 - explains counterfactual result"
  },
  "correct_reasoning": [
    "Step 1: Identify the causal structure",
    "Step 2: Apply backdoor criterion",
    "Step 3: Compute causal effect"
  ],
  "wise_refusal": "A response demonstrating understanding of the trap (50+ chars)",
  "is_original": false,
  "original_case_ref": null
}
```

### Required Fields by Level

| Field | L1 | L2 | L3 |
|-------|----|----|----|
| case_id | ✅ | ✅ | ✅ |
| scenario | ✅ | ✅ | ✅ |
| variables | ✅ | ✅ | ✅ |
| annotations | ✅ | ✅ | ✅ |
| correct_reasoning | ✅ | ✅ | ✅ |
| wise_refusal | ✅ | ✅ | ✅ |
| is_original | ✅ | ✅ | ✅ |
| hidden_structure | ❌ | ✅ | ❌ |
| ground_truth | ❌ | ❌ | ✅ |

### Valid Trap Types

```
GOODHART, CONF_MED, INSTRUMENTAL, SELECTION, SPURIOUS, SPECIFICATION,
FEEDBACK, COUNTERFACTUAL, CLUSTERING, COMPOSITION, REGRESSION,
TRADE_OFF, CALIBRATION, INTERPRETABILITY, ALIGNMENT, MECHANISM,
METRIC, ROBUSTNESS, EXTRAPOLATION, DISTRIBUTION_SHIFT
```

### Valid Variable Roles

```
treatment, outcome, confounder, mediator, collider
```

### Valid Ground Truth Verdicts (L3)

```
VALID, INVALID, CONDITIONAL
```

---

## Validation System

### Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| CRITICAL | Structural/logical errors | Must fix, blocks acceptance |
| HIGH | Significant quality issues | Must fix |
| MEDIUM | Quality improvements needed | Recommended fix |
| LOW | Minor/stylistic suggestions | Optional fix |

### Revision Cycles

```
Case → Validation → Issues?
         │
    ┌────┴────┐
    │ No      │ Yes
    ▼         ▼
 ACCEPT    Cycle ≤ 3?
              │
         ┌────┴────┐
         │ Yes     │ No
         ▼         ▼
      REVISE    REJECT
         │
         └→ Re-validate
```

### Quality Thresholds (`config.json`)

```json
{
  "quality_thresholds": {
    "min_crit_score": 5.0,
    "target_crit_score": 7.0,
    "max_similarity": 0.75,
    "structure_pass_rate": 0.95,
    "dag_validity_rate": 0.98
  }
}
```

---

## Quality Metrics

### CRIT Score Calculation

The base implementation provides structural scoring:

```python
score = 0.0

# 1. Structural completeness (0-2 points)
if validate_case_structure(case): score += 2.0

# 2. Scenario quality (0-2 points)
if len(scenario) >= 100: score += 1.0
if len(scenario) >= 200: score += 0.5
if has_variable_references: score += 0.5

# 3. Reasoning quality (0-2 points)
if len(reasoning_steps) >= 3: score += 1.0
if len(reasoning_steps) >= 5: score += 0.5
if quality_steps >= 60%: score += 0.5

# 4. Wise refusal quality (0-2 points)
if len(refusal) >= 100: score += 1.0
if len(refusal) >= 200: score += 0.5
if references_key_insight: score += 0.5

# 5. Causal structure quality (0-2 points)
if has_arrow_notation: score += 1.0
if proper_dag_symbols: score += 0.5
if level_specific_fields: score += 0.5

return min(10.0, score)
```

### Distribution Targets

#### Pearl Levels

| Level | Min % | Max % | Description |
|-------|-------|-------|-------------|
| L1 | 10% | 12% | Association/Observation |
| L2 | 66% | 70% | Intervention/do-calculus |
| L3 | 18% | 21% | Counterfactual reasoning |

#### L3 Ground Truth

| Verdict | Target % | Description |
|---------|----------|-------------|
| VALID | 30% | Claim is true given SCM |
| INVALID | 20% | Claim is false given SCM |
| CONDITIONAL | 50% | Depends on assumptions |

---

## Deliverables

### Required Files

- [x] **`GroupI1_dataset.json`** - 454 cases in required JSON format
- [x] **`analysis_report.md`** - Analysis report with methodology documentation

### Verification Commands

```bash
# Verify total case count
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); print(f'Total: {len(d)}')"
# Expected: Total: 454

# Verify unique IDs
python3 -c "import json; d=json.load(open('project/output/final/GroupI1_dataset.json')); ids=[c['case_id'] for c in d]; print(f'Unique: {len(set(ids))}/{len(ids)}')"
# Expected: Unique: 454/454

# Verify no duplicates
python3 -c "import json; from collections import Counter; d=json.load(open('project/output/final/GroupI1_dataset.json')); ids=[c['case_id'] for c in d]; dups=[id for id,cnt in Counter(ids).items() if cnt>1]; print(f'Duplicates: {dups}')"
# Expected: Duplicates: []

# Verify Pearl distribution
python3 -c "import json; from collections import Counter; d=json.load(open('project/output/final/GroupI1_dataset.json')); print(Counter(c['annotations']['pearl_level'] for c in d))"
# Expected: Counter({'L2': 277, 'L3': 125, 'L1': 52})
```

---

## References

### Course Materials

| Source | Content |
|--------|---------|
| [CS372_Win2026_Assignment1.md](docs/course/assignments/CS372_Win2026_Assignment1.md) | Assignment requirements |
| [CS3722026-Lecture2.md](docs/course/lectures/CS3722026-Lecture2.md) | Pearl's Ladder, backdoor criterion |
| [chapter6and7.md](docs/course/readings/chapter6and7.md) | SocraSynth/EVINCE, CRIT algorithm |

### Original Benchmark

| Source | Content |
|--------|---------|
| [BenchmarkT3-BucketLarge-I.md](docs/data/BenchmarkT3-BucketLarge-I.md) | Original 49 cases |

### Academic References

- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.)
- Pearl, J., Glymour, M., & Jewell, N. P. (2016). *Causal Inference in Statistics: A Primer*
- Pearl, J. & Mackenzie, D. (2018). *The Book of Why*
- Course readings on SocraSynth.com

---

## License

This project is for educational purposes as part of Stanford CS372 Winter 2026: Path to AGI.

---

*Generated by T3 Benchmark Orchestrator - January 9, 2026*
