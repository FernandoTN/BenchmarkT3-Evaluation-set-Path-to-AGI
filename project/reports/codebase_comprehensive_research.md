---
date: 2026-01-10T03:14:05Z
researcher: Claude Opus 4.5
git_commit: 0d50346136dc458f30a7e19f67d45a42410f9384
branch: main
repository: AGI
topic: "Comprehensive Codebase Analysis: T3 Benchmark Expansion Project"
tags: [research, codebase, orchestrator, generators, validators, benchmark, causal-reasoning, ai-safety]
status: complete
last_updated: 2026-01-10
last_updated_by: Claude Opus 4.5
---

# Research: Comprehensive Codebase Analysis

**Date**: 2026-01-10T03:14:05Z
**Researcher**: Claude Opus 4.5
**Git Commit**: 0d50346136dc458f30a7e19f67d45a42410f9384
**Branch**: main
**Repository**: AGI

## Research Question

Document the complete codebase structure, architecture, and implementation of the T3 Benchmark Expansion Project.

## Executive Summary

The AGI project is a **CS372 course assignment** for expanding the T3Benchmark dataset from 45 original cases to 450 total cases. The project implements a master orchestrator architecture with 8 specialized generators, 3 validators, and comprehensive quality assurance using Pearl's Ladder of Causation and CRIT scoring framework.

### Key Metrics (Current State)
| Metric | Value |
|--------|-------|
| Total Cases in Final Dataset | 218 |
| Original Cases | 49 (22.5%) |
| Generated Cases | 169 (77.5%) |
| Target Total | 450 |
| Shortfall | 232 cases |
| Average CRIT Score | 8.38/10 |
| Validation Pass Rate | 87.1% |
| DAG Validity Rate | 96.2% |

---

## Project Structure

```
AGI/
├── README.md                           # Project overview
├── TODO.md                             # Task tracking
├── docs/
│   ├── course/
│   │   ├── assignments/                # CS372 assignment specs
│   │   ├── lectures/                   # Pearl's Ladder, backdoor criterion
│   │   └── readings/                   # SocraSynth/EVINCE framework
│   ├── data/
│   │   └── BenchmarkT3-BucketLarge-I.md  # Original 45 cases
│   └── plans/
│       └── archivedPlans/              # Implementation plans
├── project/
│   ├── orchestrator/                   # Pipeline coordination
│   │   ├── orchestrator.py             # Main coordinator (~1763 lines)
│   │   ├── config.json                 # Configuration
│   │   └── progress_tracker.json       # State tracking
│   ├── generators/                     # Case generation
│   │   ├── base_generator.py           # Abstract base class
│   │   ├── crit_evaluator.py           # Quality scoring
│   │   ├── diversity_enforcer.py       # Duplicate detection
│   │   └── gen_01-08_*.py              # 8 category generators
│   ├── validators/                     # Validation logic
│   │   ├── dag_validator.py            # DAG structure validation
│   │   ├── content_validator.py        # CRIT rubric scoring
│   │   └── cross_validator.py          # Distribution verification
│   ├── categories/                     # Original case data
│   │   └── {trap_type}/original.json   # Cases by category
│   ├── schemas/
│   │   └── case_schema.json            # JSON schema
│   ├── instructions/                   # Methodology docs
│   │   ├── MASTER_INSTRUCTIONS.md
│   │   ├── PEARL_LEVELS.md
│   │   ├── TRAP_TYPES.md
│   │   ├── CASE_TEMPLATE.md
│   │   └── CAUSAL_STRUCTURES.md
│   └── output/                         # Generated outputs
│       ├── generated/                  # Batch outputs
│       ├── validated/                  # Passed validation
│       ├── revision/                   # Failed cases
│       ├── final/                      # Final dataset
│       └── analysis_report.md
└── scripts/                            # Utility scripts
```

---

## Core Components

### 1. Orchestrator System

**Location**: `project/orchestrator/orchestrator.py`

The orchestrator is the main pipeline coordinator implementing a 4-phase workflow:

#### Pipeline Phases

1. **GENERATION** (lines 500-563)
   - Distributes work to 8 specialized generators
   - Allocates cases based on config targets
   - Adds `_generator_id` tracking to each case

2. **VALIDATION** (lines 817-986)
   - Runs DAG validation (acyclicity, backdoor criterion)
   - Runs content validation (CRIT scoring)
   - Runs cross-validation (duplicates, distribution)
   - Categorizes issues by severity (CRITICAL/HIGH/MEDIUM/LOW)

3. **REVISION** (lines 988-1137)
   - Processes cases with CRITICAL/HIGH issues
   - Applies targeted fixes (expand scenarios, add reasoning)
   - Re-validates up to 3 cycles per case

4. **FINALIZATION** (lines 1208-1275)
   - Merges validated cases with original 45
   - Generates final dataset and analysis report

#### Key Classes

| Class | Lines | Purpose |
|-------|-------|---------|
| `PipelinePhase` | 108-116 | Enum for pipeline phases |
| `PhaseStatus` | 119-125 | Status tracking (PENDING/IN_PROGRESS/COMPLETED/FAILED) |
| `IssueSeverity` | 128-134 | Validation severity levels |
| `ValidationIssue` | 142-160 | Represents validation issues |
| `RevisionQueueItem` | 164-180 | Items queued for revision |
| `PipelineStats` | 184-222 | Overall statistics tracking |
| `Orchestrator` | 230-1610 | Main coordinator class |

#### Configuration (`config.json`)

```json
{
  "total_target_cases": 450,
  "new_cases_to_generate": 405,
  "original_cases": 45,
  "quality_thresholds": {
    "min_crit_score": 5.0,
    "target_crit_score": 7.0,
    "max_similarity": 0.85,
    "structure_pass_rate": 0.95,
    "dag_validity_rate": 0.98
  }
}
```

---

### 2. Generator System

**Location**: `project/generators/`

#### Base Generator (`base_generator.py`)

Abstract base class providing:

- **Enums** (lines 30-48): PearlLevel (L1/L2/L3), Difficulty, GroundTruthVerdict
- **Data Classes** (lines 111-177): GenerationStats, CRITResult
- **Pearl Level Distributions** (lines 52-61): Default distributions per trap type
- **CRIT Integration** (lines 674-837): Quality scoring on 0-10 scale

Key methods:
- `_create_case_template()` (lines 363-412): Skeleton case creation
- `_assign_pearl_level()` (lines 414-482): Weighted random selection
- `_validate_case_structure()` (lines 585-672): Format validation
- `_calculate_crit_score()` (lines 678-757): Content quality scoring

#### CRIT Evaluator (`crit_evaluator.py`)

Implements CRIT (Critical Reading Inquisitive Template) scoring:

**Dimension Weights** (lines 161-169):
| Dimension | Weight |
|-----------|--------|
| scenario_clarity | 0.15 |
| variable_definition | 0.10 |
| trap_mechanism | 0.25 |
| reasoning_chain | 0.20 |
| wise_refusal | 0.15 |
| claim_validity | 0.10 |
| counter_strength | 0.05 |

**Thresholds** (lines 138-145):
- Claim clarity: min 6/10, target 8/10
- Supporting reasons: min 6/10, target 7/10
- Counter-reasons: min 7/10, target 8/10
- Overall Gamma: min 6.0, target 7.5

#### Diversity Enforcer (`diversity_enforcer.py`)

Prevents duplicates using multiple similarity metrics:

- **Jaccard similarity** (word-level)
- **N-gram similarity** (character trigrams)
- **TF-IDF cosine similarity**

Default threshold: 0.85 max similarity

Key methods:
- `check_similarity()` (lines 99-155): Evaluate case diversity
- `find_duplicates()` (lines 515-561): O(n²) pairwise comparison
- `filter_diverse_batch()` (lines 873-911): Filter new cases

#### Category Generators (gen_01 through gen_08)

| Generator | File | Target | Trap Type | Pearl L2% |
|-----------|------|--------|-----------|-----------|
| gen_01_goodhart | 1174 lines | 82 cases | GOODHART | 85% |
| gen_02_counterfactual | 1164 lines | 82 cases | COUNTERFACTUAL | 10% (L3 focused) |
| gen_03_conf_med | 810 lines | 36 cases | CONF_MED | 70% |
| gen_04_instrumental | 835 lines | 37 cases | INSTRUMENTAL | 75% |
| gen_05_selection_spurious | 1142 lines | 43 cases | SELECTION_SPURIOUS | 65% |
| gen_06_specification | ~900 lines | 37 cases | SPECIFICATION | 75% |
| gen_07_feedback_loops | ~800 lines | 28 cases | FEEDBACK | 70% |
| gen_08_other_traps | ~850 lines | 60 cases | Multiple (12 types) | 65% |

Each generator:
- Inherits from `BaseGenerator`
- Maintains subdomain-specific templates
- Implements `generate_batch()` method
- Tracks Pearl level and difficulty distributions

---

### 3. Validator System

**Location**: `project/validators/`

#### DAG Validator (`dag_validator.py`)

Validates causal DAG structures using Pearl's criteria:

**Validation Rules**:

| Rule | Severity | Lines | Purpose |
|------|----------|-------|---------|
| DAG-01 | CRITICAL | 315-364 | Acyclicity check (DFS) |
| DAG-02 | HIGH | 402-502 | Backdoor criterion validation |
| DAG-03 | HIGH | 657-730 | Collider conditioning warning |
| DAG-04 | MEDIUM | 753-865 | Variable role consistency |

Key classes:
- `DirectedGraph` (lines 54-134): Custom graph implementation
- `UndirectedGraph` (lines 137-164): For path finding

Key methods:
- `parse_structure()` (lines 197-251): Parse causal notation
- `find_backdoor_paths()` (lines 504-538): Find paths into treatment
- `is_blocked_by()` (lines 579-623): Check if path blocked by adjustment set

#### Content Validator (`content_validator.py`)

Implements CRIT rubric scoring across 5 dimensions:

**Dimensions** (all 1-10 scale):
1. **Scenario Clarity** (lines 378-449): Concreteness, action verbs
2. **Variable Definition** (lines 451-514): X, Y, Z completeness
3. **Trap Mechanism** (lines 516-575): Trap type keywords, key insight
4. **Reasoning Chain** (lines 577-665): Step count, logical flow
5. **Wise Refusal** (lines 667-749): Understanding demonstration

**Pearl Level-Specific Validation**:
- L1 (lines 751-799): Association/correlation focus
- L2 (lines 801-838): Requires `hidden_structure` field
- L3 (lines 840-888): Requires `ground_truth` field with verdict

#### Cross Validator (`cross_validator.py`)

Validates dataset-level properties:

Key checks:
- Exact duplicates (lines 318-344)
- Semantic duplicates (lines 346-384): 0.85 threshold
- Pearl level distribution (lines 462-518)
- Trap type distribution (lines 520-578)
- L3 ground truth distribution (lines 618-691)
- Subdomain coverage (lines 693-729)
- Original cases preservation (lines 731-769)

---

### 4. Case Schema

**Location**: `project/schemas/case_schema.json`

```json
{
  "required": ["case_id", "scenario", "variables", "annotations",
               "correct_reasoning", "wise_refusal", "is_original"],
  "properties": {
    "case_id": "^8\\.[0-9]{1,3}$",
    "scenario": {"minLength": 10, "maxLength": 500},
    "variables": {"X", "Y", "Z" with name/role},
    "annotations": {
      "pearl_level": ["L1", "L2", "L3"],
      "domain": "D8",
      "trap_type": [20 types],
      "trap_subtype": "string",
      "difficulty": ["Easy", "Medium", "Hard"],
      "subdomain": "string",
      "causal_structure": "DAG notation",
      "key_insight": "string"
    },
    "hidden_structure": "required for L2",
    "ground_truth": "required for L3 with verdict/justification"
  }
}
```

---

### 5. Original Case Data

**Location**: `project/categories/`

**Total Original Cases**: 49 (marked with `is_original: true`)

**Distribution by Trap Type**:
| Trap Type | Count | Percentage |
|-----------|-------|------------|
| COUNTERFACTUAL | 10 | 20.4% |
| GOODHART | 8 | 16.3% |
| SELECTION/SPURIOUS | 6 | 12.2% |
| SPECIFICATION | 4 | 8.2% |
| CONF_MED | 3 | 6.1% |
| INSTRUMENTAL | 2 | 4.1% |
| CLUSTERING | 2 | 4.1% |
| FEEDBACK | 1 | 2.0% |
| Other (11 types) | 13 | 26.5% |

**Pearl Level Distribution**:
| Level | Count | Percentage |
|-------|-------|------------|
| L1 (Association) | 7 | 14.3% |
| L2 (Intervention) | 28 | 57.1% |
| L3 (Counterfactual) | 10 | 20.4% |

---

### 6. Instruction Documents

**Location**: `project/instructions/`

| File | Purpose | Key Content |
|------|---------|-------------|
| MASTER_INSTRUCTIONS.md | Overall methodology | SocraSynth/EVINCE integration, case generation workflow |
| PEARL_LEVELS.md | Pearl's Ladder guide | L1/L2/L3 definitions, backdoor criterion, counterfactual algorithm |
| TRAP_TYPES.md | Trap taxonomy | 8 major trap types with 25+ subtypes |
| CASE_TEMPLATE.md | JSON output format | Required fields, validation criteria |
| CAUSAL_STRUCTURES.md | DAG patterns | Variable roles, arrow notation, common patterns |

---

## Theoretical Framework

### Pearl's Ladder of Causation

| Level | Query | Question | Data Required |
|-------|-------|----------|---------------|
| L1 (Association) | P(Y\|X) | "What if I see X?" | Observational |
| L2 (Intervention) | P(Y\|do(X)) | "What if I do X?" | Causal graph |
| L3 (Counterfactual) | P(Y_x\|X',Y') | "What if X had been different?" | Full SCM |

### CRIT Framework (from SocraSynth)

- **C**larity: Scenario is unambiguous
- **R**elevance: Applicable to AI Safety
- **I**nsight: Reveals non-trivial principle
- **T**estability: Clear correct/incorrect criteria

### Trap Types Taxonomy

8 major categories:
1. **Goodhart's Law**: Proxy gaming, specification gaming, perverse instantiation
2. **Conf-Med**: Correlation vs causation, proxy discrimination
3. **Instrumental**: Convergent goals, self-preservation, resource acquisition
4. **Selection/Spurious**: Selection bias, data leakage, shortcut learning
5. **Specification**: Literal interpretation, distributional shift, sim-to-real gap
6. **Feedback Loops**: Self-fulfilling prediction, performative prediction
7. **Counterfactual**: Wishful thinking, defense efficacy, causal isolation
8. **Other**: Clustering, composition, calibration, interpretability, etc.

---

## Output Files

**Location**: `project/output/`

### Final Dataset

**File**: `output/final/GroupI1_dataset.json`
- **Cases**: 218 total (49 original + 169 generated)
- **Format**: JSON array

### Statistics

| Category | Count |
|----------|-------|
| Cases Generated | 240 |
| Cases Validated | 225 |
| Cases Failed | 15 |
| Cases in Final Dataset | 218 |

### Pearl Level Distribution (Final)

| Level | Count | Percentage | Target |
|-------|-------|------------|--------|
| L1 | 35 | 16.1% | 10-12% |
| L2 | 135 | 61.9% | 66-70% |
| L3 | 48 | 22.0% | 18-21% |

### Revision Statistics

| Metric | Value |
|--------|-------|
| Total Revisions | 216 |
| Cycle 1 | 186 |
| Cycle 2 | 15 |
| Cycle 3 | 30 |
| CRITICAL Issues | 5 |
| HIGH Issues | 42 |
| MEDIUM Issues | 101 |

---

## Code References

### Orchestrator
- `project/orchestrator/orchestrator.py:230-1610` - Main Orchestrator class
- `project/orchestrator/orchestrator.py:426-498` - `run_full_pipeline()` method
- `project/orchestrator/orchestrator.py:817-986` - Validation phase
- `project/orchestrator/orchestrator.py:988-1137` - Revision phase

### Generators
- `project/generators/base_generator.py:277-945` - BaseGenerator class
- `project/generators/base_generator.py:678-757` - `_calculate_crit_score()`
- `project/generators/crit_evaluator.py:219-383` - `evaluate_case()` method
- `project/generators/diversity_enforcer.py:99-155` - `check_similarity()`

### Validators
- `project/validators/dag_validator.py:315-364` - DAG-01 acyclicity check
- `project/validators/dag_validator.py:402-502` - DAG-02 backdoor criterion
- `project/validators/content_validator.py:378-749` - Dimension scoring
- `project/validators/cross_validator.py:136-230` - Main validate method

### Schemas
- `project/schemas/case_schema.json:1-217` - Complete case schema

---

## Current State and Known Issues

### Shortfall Analysis

The project currently has 218 cases against a target of 450 (232 shortfall).

**Root Causes** (from `TODO.md`):

| Generator | Target | Generated | Gap | Issue |
|-----------|--------|-----------|-----|-------|
| gen_01_goodhart | 82 | 32 | -50 | Only 10 templates |
| gen_02_counterfactual | 82 | 14 | -68 | L3 complexity limits reuse |
| gen_03_conf_med | 36 | 12 | -24 | Dynamic generation |
| gen_04_instrumental | 37 | 14 | -23 | Constrained scenarios |

**Issues Fixed**:
- Case ID 8.341 appeared 155 times (now unique)
- 56 duplicate scenarios removed (274 → 218 cases)

### Quality Achievements

All quality targets met:
- Mean CRIT score: 8.38 (target: ≥7.0)
- Validation pass rate: 87.1% (target: ≥70%)
- DAG validity rate: 96.2% (target: ≥95%)
- Duplicate rate: 0% (target: 0%)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ GENERATION  │→ │ VALIDATION  │→ │  REVISION   │→ FINAL   │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└────────┬────────────────┬─────────────────┬─────────────────┘
         │                │                 │
         ▼                ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   GENERATORS    │ │   VALIDATORS    │ │   QUALITY       │
│  ┌───────────┐  │ │  ┌───────────┐  │ │  ┌───────────┐  │
│  │ Goodhart  │  │ │  │    DAG    │  │ │  │   CRIT    │  │
│  ├───────────┤  │ │  ├───────────┤  │ │  │ Evaluator │  │
│  │ Counter-  │  │ │  │  Content  │  │ │  ├───────────┤  │
│  │ factual   │  │ │  ├───────────┤  │ │  │ Diversity │  │
│  ├───────────┤  │ │  │   Cross   │  │ │  │ Enforcer  │  │
│  │  ConfMed  │  │ │  └───────────┘  │ │  └───────────┘  │
│  ├───────────┤  │ └─────────────────┘ └─────────────────┘
│  │Instrument │  │
│  ├───────────┤  │        ┌─────────────────────────────┐
│  │ Selection │  │        │     CASE SCHEMA             │
│  ├───────────┤  │        │  ┌─────────────────────┐    │
│  │   Spec    │  │        │  │ case_id, scenario   │    │
│  ├───────────┤  │        │  │ variables (X,Y,Z)   │    │
│  │ Feedback  │  │        │  │ annotations         │    │
│  ├───────────┤  │        │  │ correct_reasoning   │    │
│  │  Other    │  │        │  │ wise_refusal        │    │
│  └───────────┘  │        │  │ hidden_structure    │    │
└─────────────────┘        │  │ ground_truth (L3)   │    │
                           │  └─────────────────────┘    │
                           └─────────────────────────────┘
```

---

## Related Documentation

- `project/reports/generation_shortfall_analysis.md` - Root cause analysis
- `project/output/analysis_report.md` - Pipeline execution report
- `docs/plans/archivedPlans/memoized-beaming-barto.md` - Implementation plan

---

## Open Questions

1. How to expand template pools for gen_01-04 to reach 450 target?
2. Should diversity threshold be lowered from 0.85 to 0.75?
3. Multi-pass generation with different seeds - implementation strategy?
4. LLM-based generation for remaining 42+ cases?

---

*Research document generated by comprehensive codebase analysis using parallel exploration agents.*
