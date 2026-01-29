---
date: 2026-01-22T08:30:00-08:00
researcher: Claude
git_commit: f76618a01719e7d3e373eecd70e5d6f83b1f91d2
branch: main
repository: BenchmarkT3-Evaluation-set-Path-to-AGI
topic: "Complete Codebase Documentation"
tags: [research, codebase, t3-benchmark, causal-reasoning, ai-safety]
status: complete
last_updated: 2026-01-22
last_updated_by: Claude
---

# Research: Complete Codebase Documentation

**Date**: 2026-01-22T08:30:00-08:00
**Researcher**: Claude
**Git Commit**: f76618a01719e7d3e373eecd70e5d6f83b1f91d2
**Branch**: main
**Repository**: BenchmarkT3-Evaluation-set-Path-to-AGI

## Research Question

Comprehensive documentation of the entire AGI codebase - its purpose, architecture, components, and how they interact.

## Summary

This repository is a **T3 Benchmark Expansion Project** for Stanford CS372 (Winter 2026). It expands a causal reasoning benchmark dataset from **49 original cases to 454 validated cases** for evaluating AI systems' ability to recognize "reasoning traps" - common fallacies in causal inference.

The project implements:
- **Pearl's Ladder of Causation** (L1: Association, L2: Intervention, L3: Counterfactual)
- **CRIT Scoring Framework** (Causal Reasoning Integrity Test)
- **Master Orchestrator Pipeline** coordinating 8 generators and 3 validators
- **Hybrid generation approach** (automated + agent-based gap filling)

---

## Detailed Findings

### 1. Project Purpose & Context

| Attribute | Value |
|-----------|-------|
| Course | CS372 - Winter 2026 |
| Domain | AI & Technology (D8) - AI Safety & Alignment |
| Original Cases | 49 |
| Final Cases | 454 |
| Status | COMPLETED (January 9, 2026) |

The benchmark tests AI systems on their ability to:
- Distinguish correlation from causation (L1)
- Apply do-calculus and identify backdoor paths (L2)
- Reason about counterfactual scenarios (L3)

### 2. Directory Structure

```
AGI/
├── README.md                    # Project documentation (686 lines)
├── TODO.md                      # Task tracking
├── docs/
│   ├── course/
│   │   ├── assignments/         # CS372_Win2026_Assignment1.md
│   │   ├── lectures/            # Pearl's Ladder, backdoor criterion
│   │   └── readings/            # SocraSynth/CRIT algorithm
│   ├── data/
│   │   └── BenchmarkT3-BucketLarge-I.md  # Original 49 cases
│   └── research/                # Research documents (this file)
├── project/
│   ├── orchestrator/
│   │   ├── orchestrator.py      # Main pipeline coordinator (1870 lines)
│   │   ├── config.json          # Target distributions, thresholds
│   │   └── progress_tracker.json
│   ├── generators/              # 8 trap-type-specific generators
│   ├── validators/              # 3 validation modules
│   ├── instructions/            # Case templates and guidelines
│   ├── schemas/                 # JSON Schema validation
│   ├── categories/              # Original cases by trap type
│   └── output/
│       ├── final/
│       │   └── GroupI1_datasetV2.0.json  # FINAL: 454 cases
│       ├── generated/           # Batch outputs
│       ├── validated/           # Post-validation cases
│       └── analysis_report.md   # Methodology documentation
└── scripts/
    └── pdf_to_markdown.py       # Benchmark parser
```

### 3. Theoretical Framework

#### Pearl's Ladder of Causation

| Level | Query | Question | Data Required | Common Trap |
|-------|-------|----------|---------------|-------------|
| L1 | P(Y\|X) | "What if I see X?" | Observational | Correlation ≠ causation |
| L2 | P(Y\|do(X)) | "What if I do X?" | Experimental/Causal | Backdoor paths |
| L3 | P(Y_x\|X',Y') | "What if X had been different?" | Full SCM | Wishful thinking |

#### CRIT Scoring (5 Dimensions, 1-10 scale)

1. **Scenario Clarity**: Vague (1-2) → Publication-ready (9-10)
2. **Variable Definition**: Missing (1-2) → Precise formal notation (9-10)
3. **Trap Mechanism**: Invalid (1-2) → Novel, deeply instructive (9-10)
4. **Reasoning Chain**: Illogical (1-2) → Formally valid (9-10)
5. **Wise Refusal**: Wrong (1-2) → Deep understanding (9-10)

**Acceptance**: Mean CRIT score ≥ 7.0, Min score ≥ 5.0

### 4. Pipeline Architecture

```
                ┌─────────────────┐
                │   Orchestrator  │
                │   (Main Loop)   │
                └────────┬────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌───────────┐     ┌───────────┐     ┌───────────┐
│ Generation│     │ Validation│     │  Revision │
│  Phase    │     │   Phase   │     │   Phase   │
└─────┬─────┘     └─────┬─────┘     └─────┬─────┘
      │                 │                 │
 ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
 │8 Gens   │       │3 Valids │       │Max 3    │
 │(Parallel)│       │(Series) │       │Cycles   │
 └─────────┘       └─────────┘       └─────────┘
```

**Pipeline Phases**:
1. **GENERATION**: 8 parallel generators produce cases by trap type
2. **VALIDATION**: DAG + Content + Cross validators check quality
3. **REVISION**: Up to 3 cycles to fix failing cases
4. **FINALIZATION**: Merge with originals, deduplicate, output

### 5. Generators (8 Modules)

| Generator | Trap Type | Allocation | Pearl Distribution |
|-----------|-----------|------------|-------------------|
| gen_01_goodhart | GOODHART | 82 cases | L1: 5%, L2: 85%, L3: 10% |
| gen_02_counterfactual | COUNTERFACTUAL | 82 cases | L1: 0%, L2: 10%, L3: 90% |
| gen_03_conf_med | CONF_MED | 36 cases | L1: 15%, L2: 70%, L3: 15% |
| gen_04_instrumental | INSTRUMENTAL | 37 cases | L1: 5%, L2: 75%, L3: 20% |
| gen_05_selection_spurious | SELECTION_SPURIOUS | 43 cases | L1: 20%, L2: 65%, L3: 15% |
| gen_06_specification | SPECIFICATION | 37 cases | L1: 10%, L2: 75%, L3: 15% |
| gen_07_feedback_loops | FEEDBACK | 28 cases | L1: 10%, L2: 70%, L3: 20% |
| gen_08_other_traps | OTHER | 60 cases | L1: 15%, L2: 65%, L3: 20% |

Each generator:
- Extends `BaseGenerator` abstract class
- Uses template patterns with context dictionaries
- Assigns Pearl levels via probabilistic weighting
- Calculates CRIT scores for quality assessment
- Enforces diversity via similarity filtering (max 0.85)

### 6. Validators (3 Modules)

#### DAG Validator (`dag_validator.py`)

| Rule | Severity | Description |
|------|----------|-------------|
| DAG-01 | CRITICAL | Acyclicity check (no cycles allowed) |
| DAG-02 | HIGH | Backdoor criterion validation |
| DAG-03 | HIGH | Collider conditioning warnings |
| DAG-04 | MEDIUM | Variable role consistency |

Parses causal structure notation (`X -> Y <- Z`) into directed graphs and validates structural integrity.

#### Content Validator (`content_validator.py`)

Scores cases across 5 CRIT dimensions with level-specific requirements:
- **L1**: Emphasizes observational nature
- **L2**: Requires `hidden_structure` field
- **L3**: Requires `ground_truth` with verdict (VALID/INVALID/CONDITIONAL)

#### Cross Validator (`cross_validator.py`)

- **Exact duplicates**: Normalized text comparison
- **Semantic duplicates**: 60% SequenceMatcher + 40% n-gram overlap (threshold: 0.75)
- **Distribution checks**: Pearl levels, trap types, difficulty, L3 verdicts
- **Placeholder detection**: Identifies incomplete cases

### 7. Case Schema

```json
{
  "case_id": "8.123",
  "scenario": "Description of AI safety scenario (10-500 chars)",
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
  "hidden_structure": "Required for L2",
  "ground_truth": {"verdict": "CONDITIONAL", "justification": "..."}, // L3 only
  "correct_reasoning": ["Step 1...", "Step 2...", "Step 3..."],
  "wise_refusal": "Response demonstrating understanding of the trap"
}
```

### 8. Trap Type Taxonomy (20 Types)

**Primary Categories:**
1. **GOODHART** (6 subtypes): Proxy Gaming, Specification Gaming, Misaligned Proxy, Constraint Violation, Perverse Instantiation, Metric Optimization
2. **CONF_MED** (4 subtypes): Correlation vs Causation, Proxy Discrimination, Causal Confusion, Spurious Correlation
3. **INSTRUMENTAL** (3 subtypes): Instrumental Convergence, Self-Preservation, Resource Acquisition
4. **SELECTION_SPURIOUS** (4 subtypes): Selection Bias, Data Leakage, Elicitation Confounding, Clever Hans
5. **SPECIFICATION** (4 subtypes): Literal Interpretation, Distributional Shift, Sim-to-Real Gap, Outcome Manipulation
6. **FEEDBACK** (2 subtypes): Self-Fulfilling Prediction, Performative Prediction
7. **COUNTERFACTUAL** (4 subtypes): Wishful Thinking, Defense Efficacy, Causal Isolation, Substitution Effect
8. **OTHER** (8 subtypes): Clustering, Composition, Regression, Trade-Off, Calibration, Interpretability, Alignment, Mechanism

### 9. Final Dataset Statistics

| Metric | Target | Achieved |
|--------|--------|----------|
| Total Cases | 454 | 454 |
| Unique IDs | 100% | 100% |
| Mean CRIT Score | ≥7.0 | 8.54 |
| DAG Validity Rate | ≥95% | 96.9% |

**Pearl Level Distribution:**
- L1 (Association): 52 cases (11.5%)
- L2 (Intervention): 277 cases (61.0%)
- L3 (Counterfactual): 125 cases (27.5%)

**Difficulty Distribution:**
- Easy: 91 cases (20.0%)
- Medium: 197 cases (43.4%)
- Hard: 166 cases (36.6%)

**Top Trap Types:**
- GOODHART: 93 cases (20.5%)
- COUNTERFACTUAL: 91 cases (20.0%)
- SELECTION_SPURIOUS: 47 cases (10.4%)

### 10. Implementation Approach

The project used a **hybrid approach**:

| Phase | Description | Result |
|-------|-------------|--------|
| Phase 1 | Bug fixes (duplicate IDs, schema errors) | Infrastructure ready |
| Phase 2-3 | Automated pipeline (0.75 similarity threshold) | 281 cases |
| Phase 4 | Agent-based gap filling (4 parallel agents) | +173 cases |
| Phase 5 | Final validation and assembly | 454 cases |

---

## Code References

- `project/orchestrator/orchestrator.py` - Main pipeline coordinator (1870 lines)
- `project/generators/base_generator.py` - Abstract generator base class
- `project/validators/dag_validator.py` - DAG structure validation
- `project/validators/content_validator.py` - CRIT rubric scoring
- `project/validators/cross_validator.py` - Duplicate detection
- `project/schemas/case_schema.json` - JSON Schema validation
- `project/instructions/PEARL_LEVELS.md` - L1/L2/L3 specifications
- `project/instructions/TRAP_TYPES.md` - 20 trap type taxonomy
- `project/output/final/GroupI1_datasetV2.0.json` - Final 454 cases

---

## Architecture Documentation

### Key Design Patterns

1. **Master Orchestrator**: Coordinates 8 generators and 3 validators through 4 pipeline phases
2. **Template-based Generation**: Each generator uses trap-specific templates with context dictionaries
3. **Lazy Loading**: Validators instantiated on first access to avoid circular imports
4. **Atomic ID Counter**: Thread-safe unique ID generation across concurrent generators
5. **Crash Recovery**: Checkpoint system saves state after each phase

### Data Flow

```
Original Cases (49) ──┐
                      │
Generators (8) ───────┼──→ Generated Cases
                      │         │
                      │         ▼
                      │    DAG Validator ──→ Content Validator ──→ Cross Validator
                      │         │                   │                    │
                      │         ▼                   ▼                    ▼
                      │    Revision Queue (max 3 cycles)
                      │         │
                      │         ▼
                      └──→ Final Dataset (454 cases)
```

### Technology Stack

- **Language**: Python 3.10+
- **Dependencies**: Standard library only (no external packages)
- **Testing**: pytest with coverage
- **Logging**: Python logging to console + file

---

## Historical Context

### Development Timeline

1. **January 7, 2026**: Assignment released
2. **January 8, 2026**: Group formation deadline
3. **January 9, 2026**: Project completed (454 cases achieved)
4. **January 11, 2026**: Dataset cleanup and finalization
5. **January 14, 2026**: Assignment due date

### Key Challenges Solved

1. **Template Similarity Ceiling**: Automated pipeline hit ~280 cases; agent-based writing filled remaining 173
2. **Duplicate ID Bug**: Fixed with AtomicIDCounter for thread-safe generation
3. **Schema Violations**: Added level-specific field requirements (L2: hidden_structure, L3: ground_truth)
4. **Placeholder Detection**: Cross validator identifies incomplete cases

---

## Related Research

This document provides the foundational reference for the AGI codebase. Related materials:
- `docs/course/assignments/CS372_Win2026_Assignment1.md` - Assignment requirements
- `docs/data/BenchmarkT3-BucketLarge-I.md` - Original 49 cases
- `project/output/analysis_report.md` - Generation methodology

---

## Open Questions

None at this time. The project is complete with all deliverables submitted.
