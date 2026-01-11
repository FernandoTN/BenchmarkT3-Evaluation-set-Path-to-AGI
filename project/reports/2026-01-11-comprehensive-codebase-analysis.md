# T3 Benchmark Expansion Project - Comprehensive Codebase Analysis

**Date:** 2026-01-11
**Repository:** AGI
**Branch:** main
**Commit:** 9cdebbd1b7c04cd1c77e872822edc8fcf56d53a7
**Course:** Stanford CS372 - Artificial General Intelligence (Winter 2026)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
3. [Architecture](#3-architecture)
4. [Orchestrator System](#4-orchestrator-system)
5. [Generator System](#5-generator-system)
6. [Validator System](#6-validator-system)
7. [Schema and Instructions](#7-schema-and-instructions)
8. [Data Pipeline and Output](#8-data-pipeline-and-output)
9. [Theoretical Framework](#9-theoretical-framework)
10. [File Reference](#10-file-reference)

---

## 1. Executive Summary

This document provides a comprehensive analysis of the T3 Benchmark Expansion Project codebase, a Stanford CS372 project that expands an AI safety evaluation benchmark from 49 original cases to 454 validated cases. The project implements Pearl's Ladder of Causation and the CRIT (Causal Reasoning Integrity Test) scoring framework.

### Key Metrics Achieved

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Total Cases | 454 | 454 | Complete |
| Unique Case IDs | 100% | 100% | Complete |
| Mean CRIT Score | ≥7.0 | 8.54 | Exceeded |
| DAG Validity Rate | ≥95% | 96.9% | Exceeded |
| Duplicate Rate | 0% | 0% | Complete |

### Pearl Level Distribution

| Level | Count | Percentage | Description |
|-------|-------|------------|-------------|
| L1 | 52 | 11.5% | Association (Seeing) |
| L2 | 277 | 61.0% | Intervention (Doing) |
| L3 | 125 | 27.5% | Counterfactual (Imagining) |

---

## 2. Project Overview

### 2.1 Purpose

The project expands the T3 Benchmark dataset for evaluating AI systems' causal reasoning capabilities. The benchmark focuses on identifying "reasoning traps" - common fallacies in causal inference that AI systems must recognize and avoid.

### 2.2 Assignment Context

| Attribute | Value |
|-----------|-------|
| Course | CS372 - Winter 2026 |
| Domain | AI & Technology (D8) |
| Signature Trap | Goodhart's Law |
| Focus | Association, Intervention, Counterfactual |
| Status | Completed (January 9, 2026) |

### 2.3 Implementation Strategy

The project used a hybrid approach:

| Phase | Description | Result |
|-------|-------------|--------|
| Phase 1 | Bug fixes (duplicate IDs, schema errors, placeholder detection) | Infrastructure ready |
| Phase 2-3 | Automated pipeline with 0.75 similarity threshold | 281 cases |
| Phase 4 | Agent-based gap filling (173 additional cases) | 454 cases |
| Phase 5 | Final validation and dataset assembly | 100% verified |

---

## 3. Architecture

### 3.1 System Overview

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

### 3.2 Directory Structure

```
AGI/
├── README.md                           # Project documentation
├── docs/
│   ├── course/
│   │   ├── assignments/                # CS372_Win2026_Assignment1
│   │   ├── lectures/                   # Lecture materials
│   │   └── readings/                   # SocraSynth/CRIT readings
│   └── data/
│       └── BenchmarkT3-BucketLarge-I   # Original 49 cases
├── project/
│   ├── orchestrator/                   # Main pipeline coordinator
│   │   ├── orchestrator.py             # 1870 lines
│   │   ├── config.json                 # Target distributions
│   │   └── progress_tracker.json       # Progress state
│   ├── generators/                     # 8 specialized generators
│   │   ├── base_generator.py           # Abstract base class
│   │   ├── gen_01_goodhart.py          # Goodhart's Law
│   │   ├── gen_02_counterfactual.py    # Counterfactual reasoning
│   │   ├── gen_03_conf_med.py          # Confounding/Mediation
│   │   ├── gen_04_instrumental.py      # Instrumental convergence
│   │   ├── gen_05_selection_spurious.py # Selection bias
│   │   ├── gen_06_specification.py     # Specification gaming
│   │   ├── gen_07_feedback_loops.py    # Feedback loops
│   │   ├── gen_08_other_traps.py       # Other trap types
│   │   ├── crit_evaluator.py           # CRIT scoring
│   │   └── diversity_enforcer.py       # Diversity checking
│   ├── validators/                     # 3 validators
│   │   ├── dag_validator.py            # DAG structure validation
│   │   ├── content_validator.py        # CRIT rubric scoring
│   │   └── cross_validator.py          # Duplicate detection
│   ├── instructions/                   # Generation guidelines
│   │   ├── PEARL_LEVELS.md             # L1/L2/L3 specifications
│   │   ├── TRAP_TYPES.md               # 20+ trap taxonomy
│   │   ├── CASE_TEMPLATE.md            # JSON case structure
│   │   └── CAUSAL_STRUCTURES.md        # DAG patterns
│   ├── schemas/
│   │   └── case_schema.json            # JSON Schema validation
│   ├── categories/                     # Original cases by type
│   └── output/
│       └── final/
│           └── GroupI1_dataset.json    # Final 454 cases
└── scripts/
    └── pdf_to_markdown.py              # Benchmark parser
```

---

## 4. Orchestrator System

**File:** `project/orchestrator/orchestrator.py` (1870 lines)

### 4.1 Core Classes and Enums

#### AtomicIDCounter (Lines 103-130)
Thread-safe counter for generating unique case IDs to prevent duplicates during concurrent generation.

```python
class AtomicIDCounter:
    def __init__(start: int = 100)  # Starts at 100 to avoid original cases
    def next_id() -> int            # Thread-safe unique ID
```

#### Pipeline Enums (Lines 151-177)

**PipelinePhase:**
- SETUP, GENERATION, VALIDATION, REVISION, FINALIZATION, COMPLETE

**PhaseStatus:**
- PENDING, IN_PROGRESS, COMPLETED, FAILED

**IssueSeverity:**
- CRITICAL, HIGH, MEDIUM, LOW

#### Data Classes

**ValidationIssue (Lines 185-203):**
```python
@dataclass
class ValidationIssue:
    case_id: str
    rule: str              # e.g., "DAG-01"
    severity: IssueSeverity
    message: str
    suggestion: Optional[str]
```

**RevisionQueueItem (Lines 206-223):**
```python
@dataclass
class RevisionQueueItem:
    case_id: str
    case_data: dict
    issues: list[ValidationIssue]
    revision_cycle: int    # 0-3
    generator_id: str
```

**PipelineStats (Lines 226-265):**
```python
@dataclass
class PipelineStats:
    total_generated: int
    total_validated: int
    total_accepted: int
    total_rejected: int
    crit_scores: list[float]
    validation_pass_rate: float
    dag_validity_rate: float
```

### 4.2 Orchestrator Class (Lines 273-1718)

**Class Constants:**
```python
MAX_REVISION_CYCLES = 3
TARGET_TOTAL_CASES = 450
ORIGINAL_CASES_COUNT = 45
NEW_CASES_TARGET = 405
```

**Key Methods:**

| Method | Lines | Purpose |
|--------|-------|---------|
| `run_full_pipeline()` | 472-549 | Complete pipeline execution |
| `run_generation_phase()` | 551-614 | Distribute to 8 generators |
| `run_validation_phase()` | 874-1043 | DAG + Content + Cross validation |
| `run_revision_phase()` | 1069-1218 | Max 3 revision cycles |
| `finalize_dataset()` | 1289-1383 | Merge, dedupe, output |
| `generate_report()` | 1542-1718 | Analysis report generation |

### 4.3 Pipeline Flow

```
Phase 1: Generation
    ├─ Load generator configs from config.json
    ├─ For each of 8 generators:
    │   ├─ Generate batch (allocation count)
    │   ├─ Tag with _generator_id
    │   └─ Save to output/generated/
    └─ Update stats.total_generated

Phase 2: Validation
    ├─ For each case:
    │   ├─ DAG validation (4 rules)
    │   ├─ Content validation (CRIT score)
    │   └─ Route to validated_cases or revision_queue
    ├─ Cross validation (duplicates, distributions)
    └─ Update pass rates

Phase 3: Revision
    ├─ While revision_queue not empty:
    │   ├─ If cycle > 3: Move to failed_cases
    │   ├─ Apply targeted fixes
    │   ├─ Re-validate
    │   └─ Accept or re-queue
    └─ Save failed cases

Phase 4: Finalization
    ├─ Deduplicate validated_cases
    ├─ Verify ID uniqueness
    ├─ Merge original + validated
    ├─ Sort by case_id
    └─ Save GroupI1_dataset.json
```

### 4.4 Configuration (config.json)

**Generator Allocations:**

| Generator | Trap Type | Allocation | Subdomains |
|-----------|-----------|------------|------------|
| gen_01_goodhart | GOODHART | 82 | Scaling, RLHF, Reward Hacking |
| gen_02_counterfactual | COUNTERFACTUAL | 82 | Alignment, Philosophy, Safety |
| gen_03_conf_med | CONF_MED | 36 | Medical AI, Fairness, Security |
| gen_04_instrumental | INSTRUMENTAL | 37 | Multi-Agent, Corrigibility |
| gen_05_selection_spurious | SELECTION_SPURIOUS | 43 | CV, NLP, Recommenders |
| gen_06_specification | SPECIFICATION | 37 | Autonomous Vehicles, Robotics |
| gen_07_feedback_loops | FEEDBACK | 28 | Educational AI, Social Systems |
| gen_08_other_traps | OTHER | 60 | Model Compression, Prompt Eng |

**Quality Thresholds:**
```json
{
  "min_crit_score": 5.0,
  "target_crit_score": 7.0,
  "max_similarity": 0.75,
  "structure_pass_rate": 0.95,
  "dag_validity_rate": 0.98
}
```

---

## 5. Generator System

**Directory:** `project/generators/`

### 5.1 BaseGenerator Class

**File:** `base_generator.py` (1002 lines)

#### Type Definitions (Lines 121-157)

```python
class Variable(TypedDict):
    name: str
    role: Literal["treatment", "outcome", "confounder", "mediator", "collider"]

class CaseData(TypedDict):
    case_id: str
    scenario: str
    variables: dict[str, Variable]
    annotations: Annotations
    hidden_structure: Optional[str]  # L2 only
    ground_truth: Optional[GroundTruth]  # L3 only
    correct_reasoning: list[str]
    wise_refusal: str
    is_original: bool
```

#### Abstract Methods

```python
class BaseGenerator(ABC):
    @abstractmethod
    def generate_batch(count: int, trap_type: str, subdomains: list[str]) -> list[CaseData]
```

#### Pearl Level Assignment (Lines 467-535)

Default distributions by trap type:

| Trap Type | L1 | L2 | L3 |
|-----------|----|----|-----|
| GOODHART | 5% | 80% | 15% |
| COUNTERFACTUAL | 0% | 10% | 90% |
| CONF_MED | 15% | 70% | 15% |
| INSTRUMENTAL | 5% | 75% | 20% |
| SELECTION_SPURIOUS | 20% | 65% | 15% |
| SPECIFICATION | 10% | 75% | 15% |
| FEEDBACK | 10% | 70% | 20% |
| OTHER | 15% | 65% | 20% |

#### CRIT Score Calculation (Lines 731-810)

Structural scoring (0-10 scale):
1. **Structural completeness** (0-2 pts): Required fields present
2. **Scenario quality** (0-2 pts): Length 100-200+ chars, variable references
3. **Reasoning quality** (0-2 pts): 3-5+ steps, quality indicators
4. **Wise refusal** (0-2 pts): Length 100-200+ chars, key insight reference
5. **Causal structure** (0-2 pts): Arrow notation, DAG symbols, level-specific

### 5.2 Specialized Generators

#### gen_01_goodhart.py - Goodhart's Law

**Subtypes:**
- PROXY_GAMING: Agent games the proxy measure
- SPECIFICATION_GAMING: Exploits specification gaps
- MISALIGNED_PROXY: Proxy biased relative to objective
- CONSTRAINT_VIOLATION: Violates implicit constraints
- PERVERSE_INSTANTIATION: Letter vs. spirit
- METRIC_OPTIMIZATION: Metric becomes adversarial

**Pearl Distribution:** ~5% L1, ~85% L2, ~10% L3

#### gen_02_counterfactual.py - Counterfactual Reasoning

**Subtypes:**
- WISHFUL_THINKING: Invalid counterfactual claim
- DEFENSE_EFFICACY: Evaluating intervention effectiveness
- CAUSAL_ISOLATION: Blocked causal paths
- SUBSTITUTION_EFFECT: Alternative occurrence

**Pearl Distribution:** 100% L3 (by design)

**Ground Truth Targets:**
- VALID: ~30%
- INVALID: ~20%
- CONDITIONAL: ~50%

#### gen_03_conf_med.py - Confounding & Mediation

**Subtypes:**
- CORRELATION_VS_CAUSATION: Mistake correlation for causation
- PROXY_DISCRIMINATION: Proxies encode protected attributes
- CAUSAL_CONFUSION: Learning spurious correlations
- SPURIOUS_CORRELATION: Non-causal associations

**Subdomains:** Medical AI, Fairness, Security, Algorithmic Fairness

#### gen_04_instrumental.py - Instrumental Convergence

**Subtypes:**
- INSTRUMENTAL_CONVERGENCE: Goals emergent from any terminal goal
- SELF_PRESERVATION: Agent prevents shutdown
- RESOURCE_ACQUISITION: Seeking excess resources

**Subdomains:** Multi-Agent, Corrigibility, Existential Risk

#### gen_05_selection_spurious.py - Selection Bias

**Subtypes:**
- SELECTION_BIAS: Non-random sampling
- DATA_LEAKAGE: Test data contaminates training
- ELICITATION_CONFOUNDING: Measurement method affects results
- CLEVER_HANS: Model learns spurious shortcuts
- SURVIVORSHIP_BIAS: Survivor sample nonrepresentative
- COLLIDER_BIAS: Conditioning on common effect

#### gen_06_specification.py - Specification Problems

**Subtypes:**
- LITERAL_INTERPRETATION: Letter, not spirit
- DISTRIBUTIONAL_SHIFT: Training ≠ deployment
- SIM_TO_REAL: Simulator differs from reality
- OUTCOME_MANIPULATION: Changes outcomes, not predictions
- REWARD_HACKING: Games reward function

#### gen_07_feedback_loops.py - Feedback Loops

**Subtypes:**
- SELF_FULFILLING: Prediction causes own truth
- PERFORMATIVE: Prediction changes what it predicts
- BIAS_AMPLIFICATION: Initial bias amplified
- ECHO_CHAMBER: Recommendations reinforce preferences
- DATA_DRIFT: Deployment changes distribution

#### gen_08_other_traps.py - Other Types

**Trap Types:** CLUSTERING, COMPOSITION, REGRESSION, TRADE_OFF, CALIBRATION, INTERPRETABILITY, ALIGNMENT, MECHANISM, METRIC, ROBUSTNESS, EXTRAPOLATION, DISTRIBUTION_SHIFT

### 5.3 CRIT Evaluator

**File:** `crit_evaluator.py` (1200 lines)

**Dimension Weights (Lines 160-168):**
```python
DIMENSION_WEIGHTS = {
    "scenario_clarity": 0.15,
    "variable_definition": 0.10,
    "trap_mechanism": 0.25,
    "reasoning_chain": 0.20,
    "wise_refusal": 0.15,
    "claim_validity": 0.10,
    "counter_strength": 0.05
}
```

**Score Levels:**
- EXCELLENT: ≥ 8.5
- GOOD: 7.0 - 8.5
- ACCEPTABLE: 5.0 - 7.0
- NEEDS_IMPROVEMENT: 3.0 - 5.0
- POOR: < 3.0

### 5.4 Diversity Enforcer

**File:** `diversity_enforcer.py` (1041 lines)

**Similarity Calculation:**
- Scenario similarity: 50% weight (Jaccard + n-gram + TF-IDF)
- Variable similarity: 25% weight
- Structure similarity: 25% weight

**Default threshold:** 0.85 (cases above flagged as duplicates)

---

## 6. Validator System

**Directory:** `project/validators/`

### 6.1 DAG Validator

**File:** `dag_validator.py`

**Validation Rules:**

| Rule | Severity | Description |
|------|----------|-------------|
| DAG-01 | CRITICAL | Acyclicity check (no cycles allowed) |
| DAG-02 | HIGH | Backdoor criterion validation |
| DAG-03 | HIGH | Collider conditioning warnings |
| DAG-04 | MEDIUM | Variable role consistency |

**Graph Implementation:**
- DirectedGraph (Lines 54-134): Adjacency/predecessor lists
- UndirectedGraph (Lines 137-164): Symmetric path queries

**Key Methods:**
```python
def validate(case: dict) -> list[ValidationResult]
def validate_batch(cases: list) -> dict  # Aggregate statistics
```

### 6.2 Content Validator

**File:** `content_validator.py`

**CRIT Rubric Dimensions (5 dimensions, 1-10 each):**

1. **Scenario Clarity** (Lines 378-449)
   - Length-based baseline + concrete details
   - Penalties for vague language

2. **Variable Definition** (Lines 451-514)
   - Required: X, Y, Z with names and roles
   - Bonuses for descriptive names

3. **Trap Mechanism** (Lines 516-575)
   - Valid trap type + subtype
   - Key insight quality

4. **Reasoning Chain** (Lines 577-665)
   - Step count (3-6+ steps)
   - Causal language, logical connectors

5. **Wise Refusal** (Lines 667-749)
   - Length and trap keyword coverage
   - Educational patterns

**Pearl Level Specific:**
- L1: Association/correlation focus, no intervention language
- L2: Must have `hidden_structure` (CRITICAL if missing)
- L3: Must have `ground_truth` with verdict (VALID/INVALID/CONDITIONAL)

### 6.3 Cross Validator

**File:** `cross_validator.py`

**Duplicate Detection:**
- Exact duplicates: Normalized string comparison
- Semantic duplicates: 60% SequenceMatcher + 40% n-gram overlap
- Threshold: 0.75 similarity

**Distribution Validation:**
- Pearl levels: 10-12% L1, 66-70% L2, 18-21% L3
- Trap types: Per-type min/max counts
- L3 ground truth: VALID 30%, INVALID 20%, CONDITIONAL 50%

**Placeholder Detection (Lines 788-836):**
- Empty/short variable names (<2 chars)
- "[PLACEHOLDER]" marker in scenario
- "Example ... scenario" pattern

---

## 7. Schema and Instructions

### 7.1 Case Schema

**File:** `project/schemas/case_schema.json` (JSON Schema draft-07)

**Required Fields:**
```json
{
  "case_id": "8.XXX",
  "scenario": "10-500 characters",
  "variables": {"X": {...}, "Y": {...}, "Z": {...}},
  "annotations": {
    "pearl_level": "L1|L2|L3",
    "domain": "D8",
    "trap_type": "...",
    "trap_subtype": "...",
    "difficulty": "Easy|Medium|Hard",
    "subdomain": "...",
    "causal_structure": "X -> Y <- Z",
    "key_insight": "..."
  },
  "correct_reasoning": ["Step 1...", "Step 2..."],
  "wise_refusal": "50+ characters",
  "is_original": true|false
}
```

**Conditional Fields:**
- `hidden_structure`: Required if pearl_level = L2
- `ground_truth`: Required if pearl_level = L3

**Variable Roles:** treatment, outcome, confounder, mediator, collider

**Trap Types (20):** GOODHART, CONF_MED, INSTRUMENTAL, SELECTION, SPURIOUS, SPECIFICATION, FEEDBACK, COUNTERFACTUAL, CLUSTERING, COMPOSITION, REGRESSION, TRADE_OFF, CALIBRATION, INTERPRETABILITY, ALIGNMENT, MECHANISM, METRIC, ROBUSTNESS, EXTRAPOLATION, DISTRIBUTION_SHIFT

### 7.2 Pearl Levels

**File:** `project/instructions/PEARL_LEVELS.md`

#### Level 1: Association (Seeing)
- **Query:** P(Y|X) - observational prediction
- **Question:** "What if I see X?"
- **Data:** Observational only
- **Trap:** Confusing correlation with causation

#### Level 2: Intervention (Doing)
- **Query:** P(Y|do(X)) - effect of intervention
- **Question:** "What if I do X?"
- **Data:** Experimental OR observational + causal structure
- **Trap:** Failing to identify backdoor paths

**Backdoor Criterion:**
1. No node in Z is descendant of X
2. Z blocks every path with arrow into X

#### Level 3: Counterfactual (Imagining)
- **Query:** P(Y_x|X',Y') - alternative outcomes
- **Question:** "What if X had been different?"
- **Data:** Full Structural Causal Model (SCM)
- **Trap:** Wishful thinking, defense efficacy fallacy

**Three-Step Algorithm:**
1. Abduction: Infer U from observations
2. Action: Intervene to set X=x
3. Prediction: Compute counterfactual Y_x

### 7.3 Trap Types Taxonomy

**File:** `project/instructions/TRAP_TYPES.md`

**8 Categories, 20+ Subtypes:**

1. **Goodhart's Law** (6 subtypes): Proxy Gaming, Specification Gaming, Misaligned Proxy, Constraint Violation, Perverse Instantiation, Metric Optimization

2. **Confounder/Mediator** (4 subtypes): Correlation vs Causation, Proxy Discrimination, Causal Confusion, Spurious Correlation

3. **Instrumental Convergence** (3 subtypes): Instrumental Convergence, Self-Preservation, Resource Acquisition

4. **Selection/Spurious** (4 subtypes): Selection Bias, Data Leakage, Elicitation Confounding, Clever Hans

5. **Specification** (4 subtypes): Literal Interpretation, Distributional Shift, Sim-to-Real, Outcome Manipulation

6. **Feedback Loops** (2 subtypes): Self-Fulfilling, Performative Prediction

7. **Counterfactual** (4 subtypes): Wishful Thinking, Defense Efficacy, Causal Isolation, Substitution Effect

8. **Other** (8 subtypes): Clustering, Composition, Regression, Trade-Off, Calibration, Interpretability, Alignment, Mechanism

### 7.4 Causal Structures

**File:** `project/instructions/CAUSAL_STRUCTURES.md`

**9 Fundamental Patterns:**

1. **Direct Effect:** X → Y
2. **Confounding:** X ← Z → Y
3. **Mediation:** X → M → Y
4. **Collider:** X → C ← Y
5. **M-Bias:** U₁ → X; U₂ → Y; X → Z ← Y
6. **Instrument:** I → X; X → Y; X ← U → Y
7. **Confounding + Mediation:** X ← Z → Y; X → M → Y
8. **Multiple Confounders:** X ← Z₁ → Y; X ← Z₂ → Y
9. **Time-Varying:** Z₀ → X₁ → Y₁; Z₁ → X₂ → Y₂

**Arrow Notation:**
- `→`: Direct cause
- `←`: Reverse causation
- `↔`: Bidirectional (latent confounder)
- `-/->`: No causal effect

---

## 8. Data Pipeline and Output

### 8.1 Original Cases

**File:** `project/categories/original_cases.json`

- **Total:** 49 original cases
- **L1:** 5 (10.2%)
- **L2:** 34 (69.4%)
- **L3:** 10 (20.4%)

**Category Organization (8 folders):**
- goodhart/original.json: 8 cases
- counterfactual/original.json: 10 cases
- conf_med/original.json: 3 cases
- specification/original.json: 4 cases
- selection_spurious/original.json: 4 cases
- instrumental/original.json: 2 cases
- feedback_loops/original.json: 1 case
- other_traps/original.json: 17 cases

### 8.2 Final Dataset

**File:** `project/output/final/GroupI1_dataset.json`

- **Total:** 454 cases (18,603 lines)
- **Original:** 93 cases (is_original: true)
- **Generated:** 361 cases (is_original: false)

**Trap Type Distribution:**

| Trap Type | Count | % |
|-----------|-------|---|
| GOODHART | 93 | 20.5% |
| COUNTERFACTUAL | 91 | 20.0% |
| SELECTION_SPURIOUS | 47 | 10.4% |
| SPECIFICATION | 42 | 9.3% |
| CONF_MED | 40 | 8.8% |
| INSTRUMENTAL | 39 | 8.6% |
| FEEDBACK | 30 | 6.6% |
| Other types | 72 | 15.9% |

**Difficulty Distribution:**

| Difficulty | Count | % |
|-----------|-------|---|
| Easy | 91 | 20.0% |
| Medium | 197 | 43.4% |
| Hard | 166 | 36.5% |

### 8.3 Benchmark Parser

**File:** `project/parse_benchmark.py`

**Functions:**
- `normalize_trap_type()`: Maps variations to standard enums
- `parse_benchmark_file()`: Extracts cases from markdown
- `categorize_cases()`: Organizes by trap type
- `save_json()`: Writes formatted output

---

## 9. Theoretical Framework

### 9.1 Pearl's Ladder of Causation

The T3 Benchmark uses Pearl's three-level causal hierarchy:

| Level | Query | Question | Data Required |
|-------|-------|----------|---------------|
| L1 | P(Y\|X) | "What if I see X?" | Observational |
| L2 | P(Y\|do(X)) | "What if I do X?" | Experimental + DAG |
| L3 | P(Y_x\|X',Y') | "What if X had been different?" | Full SCM |

### 9.2 CRIT Scoring Framework

**Dimensions (5):**

| Dimension | Poor (1-2) | Good (5-6) | Exceptional (9-10) |
|-----------|------------|------------|---------------------|
| Scenario Clarity | Vague | Clear | Publication-ready |
| Variable Definition | Missing | Complete | Precise formal |
| Trap Mechanism | Invalid | Non-trivial | Novel, instructive |
| Reasoning Chain | Illogical | Complete | Formally valid |
| Wise Refusal | Wrong | Correct | Deep understanding |

**Thresholds:**
- Mean ≥ 7.0: PASS
- Min ≥ 5.0: Acceptable
- Structure pass ≥ 95%

### 9.3 Course Context (CS372)

**SocraSynth Framework Principles:**
1. Multi-Perspective Analysis
2. Dialectical Reasoning
3. Structured Debate

**EVINCE Framework Components:**
- Conditional Statistics
- Contentiousness Levels (0.0-0.9)
- CRIT Algorithm (reasonableness evaluation)

---

## 10. File Reference

### Core Files

| File | Lines | Purpose |
|------|-------|---------|
| `orchestrator/orchestrator.py` | 1870 | Main pipeline coordinator |
| `orchestrator/config.json` | ~250 | Configuration settings |
| `generators/base_generator.py` | 1002 | Abstract generator base |
| `generators/crit_evaluator.py` | 1200 | CRIT scoring |
| `generators/diversity_enforcer.py` | 1041 | Diversity checking |
| `validators/dag_validator.py` | ~1000 | DAG validation |
| `validators/content_validator.py` | ~900 | Content validation |
| `validators/cross_validator.py` | ~1200 | Cross-validation |

### Specialized Generators

| File | Trap Type | Cases |
|------|-----------|-------|
| `gen_01_goodhart.py` | GOODHART | 82 |
| `gen_02_counterfactual.py` | COUNTERFACTUAL | 82 |
| `gen_03_conf_med.py` | CONF_MED | 36 |
| `gen_04_instrumental.py` | INSTRUMENTAL | 37 |
| `gen_05_selection_spurious.py` | SELECTION_SPURIOUS | 43 |
| `gen_06_specification.py` | SPECIFICATION | 37 |
| `gen_07_feedback_loops.py` | FEEDBACK | 28 |
| `gen_08_other_traps.py` | OTHER | 60 |

### Documentation Files

| File | Content |
|------|---------|
| `instructions/PEARL_LEVELS.md` | Pearl's Ladder specifications |
| `instructions/TRAP_TYPES.md` | 20+ trap taxonomy |
| `instructions/CASE_TEMPLATE.md` | JSON case format |
| `instructions/CAUSAL_STRUCTURES.md` | DAG patterns |
| `schemas/case_schema.json` | JSON Schema validation |

### Output Files

| File | Content |
|------|---------|
| `output/final/GroupI1_dataset.json` | 454 validated cases |
| `output/analysis_report.md` | Methodology documentation |
| `categories/original_cases.json` | 49 original cases |

---

*Report generated: 2026-01-11*
*T3 Benchmark Expansion Project - Stanford CS372 Winter 2026*
