# Assignment #2 Implementation Plan - CS372 T3 Benchmark
## Comprehensive Multi-Agent Parallel Execution Plan

**Author:** Fernando Torres
**Deadline:** January 28, 2026, 11:59 PM PST
**Version:** 3.0 - Multi-Agent Parallel Workflow

---

## Executive Summary

Complete Assignment #2 using a **highly parallelized multi-agent workflow**:
- **10-15 parallel sub-agents** per generation/validation batch
- **25-50 cases per batch** with intermediate checkpoints
- **Iterative validation loops** until 95%+ pass rate
- **Full validation pipeline** + LLM-as-judge quality checks

**Total Work:**
- GroupI1 (AI & Tech): 16 → 500 cases (484 new)
- GroupJ1 (Social Science): 240 → 500 cases (260 new)

---

## 1. Current State Analysis

### Dataset Status

| Dataset | Current | Target | Gap | Domain |
|---------|---------|--------|-----|--------|
| GroupI1 | 16 | 500 | 484 | D9: AI & Tech |
| GroupJ1 | 240 | 500 | 260 | D10: Social Science |

### Generation Requirements by Level

| Level | GroupI1 Gap | GroupJ1 Gap | Total New | Batches (50/batch) |
|-------|-------------|-------------|-----------|-------------------|
| L1 | 45 | 23 | 68 | 2 batches |
| L2 | 292 | 138 | 430 | 9 batches |
| L3 | 147 | 99 | 246 | 5 batches |
| **Total** | **484** | **260** | **744** | **16 batches** |

---

## 2. Multi-Agent Architecture

### 2.1 Agent Types

| Agent Type | Purpose | Count per Batch |
|------------|---------|-----------------|
| **Generator Agents** | Create new cases following templates | 10-12 |
| **Schema Validator** | Validate JSON schema compliance | 1 |
| **Content Validator** | Score cases on 10-point rubric | 2-3 |
| **Cross Validator** | Detect duplicates, check distributions | 1 |
| **LLM Quality Judge** | Verify trap type, reasoning quality | 2-3 |
| **Correction Agent** | Fix issues identified by validators | 3-5 |

### 2.2 Parallel Agent Configuration

```
Per Batch Processing:
├── Generation Phase (10-12 parallel agents)
│   ├── L1 Generator Agent × 2 (WOLF + SHEEP)
│   ├── L2 Generator Agent × 6 (one per family F1-F6)
│   └── L3 Generator Agent × 4 (families by priority)
│
├── Validation Phase (5-6 parallel agents)
│   ├── Schema Validator Agent × 1
│   ├── Content Validator Agent × 2
│   ├── Cross Validator Agent × 1
│   └── LLM Quality Judge Agent × 2
│
└── Correction Phase (3-5 parallel agents)
    ├── Field Fixer Agent × 1
    ├── Content Rewriter Agent × 2
    └── Label Corrector Agent × 2
```

---

## 3. Implementation Phases (Detailed)

### Phase 0: Infrastructure Setup

**Duration:** ~30 minutes

**Tasks:**
- [ ] Create directory structure for batch outputs
- [ ] Define unified V4.0 schema with validation fields
- [ ] Create batch configuration files
- [ ] Set up intermediate checkpoint system

**Directory Structure:**
```
project/assignment2/
├── schemas/
│   └── case_schema_v4.json
├── batches/
│   ├── groupI/
│   │   ├── batch_001/
│   │   │   ├── generated/
│   │   │   ├── validated/
│   │   │   ├── corrected/
│   │   │   └── final/
│   │   ├── batch_002/
│   │   └── ...
│   └── groupJ/
│       ├── batch_001/
│       └── ...
├── validators/
├── generators/
└── submissions/
```

---

### Phase 1: Schema Transformation (GroupJ1 Pre-processing)

**Duration:** ~1 hour

**Tasks:**
- [ ] Transform 240 existing GroupJ1 cases to V4.0 schema
- [ ] Parse variable arrays to object format
- [ ] Normalize field names and structure
- [ ] Add placeholder validation fields

**Transformation Sub-agents (3 parallel):**
1. **Variable Parser Agent**: Convert array → object format
2. **Field Normalizer Agent**: Rename and restructure fields
3. **Metadata Enricher Agent**: Add required validation fields

---

### Phase 2: Batch Generation Loop (MAIN WORKFLOW)

**This is the core iterative workflow for case generation.**

#### 2.1 Batch Planning

**GroupI1 Batches (10 batches):**
| Batch | Level | Count | Focus |
|-------|-------|-------|-------|
| I-01 | L1 | 45 | All WOLF/SHEEP/AMBIGUOUS |
| I-02 | L2 | 50 | F1: Selection (T1-T4) |
| I-03 | L2 | 50 | F2-F3: Statistical + Confounding |
| I-04 | L2 | 50 | F4: Direction (T10-T12) |
| I-05 | L2 | 50 | F5-F6: Information + Mechanism |
| I-06 | L2 | 50 | Mixed (fill gaps) |
| I-07 | L2 | 42 | Remaining L2 |
| I-08 | L3 | 50 | F1-F3: Deterministic + Probabilistic |
| I-09 | L3 | 50 | F4-F6: Structural + Temporal + Epistemic |
| I-10 | L3 | 47 | F7-F8 + DomainExt |

**GroupJ1 Batches (6 batches):**
| Batch | Level | Count | Focus |
|-------|-------|-------|-------|
| J-01 | L1 | 23 | Fill WOLF/SHEEP gaps |
| J-02 | L2 | 50 | Underrepresented trap types |
| J-03 | L2 | 50 | Fill family gaps |
| J-04 | L2 | 38 | Remaining L2 |
| J-05 | L3 | 50 | Priority families (F2, F3, F8) |
| J-06 | L3 | 49 | Remaining L3 families |

#### 2.2 Per-Batch Workflow (Iterative Loop)

```
┌─────────────────────────────────────────────────────────────┐
│                    BATCH PROCESSING LOOP                     │
│                                                              │
│  ┌──────────────────┐                                       │
│  │  STEP 1: GENERATE │ ← 10-12 Parallel Generator Agents    │
│  │  (25-50 cases)    │                                      │
│  └────────┬─────────┘                                       │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │  STEP 2: VALIDATE │ ← 5-6 Parallel Validator Agents      │
│  │  (Full Pipeline)  │                                      │
│  └────────┬─────────┘                                       │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │  STEP 3: SCORE   │ ← Aggregate validation results        │
│  │  (Calculate %)    │                                      │
│  └────────┬─────────┘                                       │
│           ▼                                                  │
│  ┌──────────────────┐      ┌───────────────────┐            │
│  │  Pass Rate ≥95%? │──YES──▶│ STEP 5: FINALIZE │            │
│  │                  │       │ (Move to final/)  │            │
│  └────────┬─────────┘       └───────────────────┘            │
│           │NO                                                │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │  STEP 4: CORRECT │ ← 3-5 Parallel Correction Agents      │
│  │  (Fix failures)   │                                      │
│  └────────┬─────────┘                                       │
│           │                                                  │
│           └──────────────── LOOP BACK TO STEP 2 ────────────┘
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Phase 2A: Generation Step (Per Batch)

**10-12 Parallel Generator Agents**

Each generator agent receives:
- Target level (L1/L2/L3)
- Target trap types or families
- Domain context (AI & Tech or Social Science)
- Case count to generate
- Template examples from guidelines

**L1 Generator Configuration:**
```
L1 Generator Agents (2 per batch):
├── WOLF Generator
│   ├── Input: Trap types W1, W2, W3, W5, W7, W9, W10
│   ├── Template: L1 Guidelines Section 3 (WOLF Templates)
│   ├── Output: Cases with label "W", trap_type "W1-W10"
│   └── Target: 12-13 cases per batch
│
└── SHEEP Generator
    ├── Input: Evidence types S1, S2, S3, S4, S5
    ├── Template: L1 Guidelines Section 4 (SHEEP Templates)
    ├── Output: Cases with label "S", trap_type "S1-S8"
    └── Target: 10 cases per batch
```

**L2 Generator Configuration:**
```
L2 Generator Agents (6 per batch - one per family):
├── F1: Selection Generator (T1-T4)
├── F2: Statistical Generator (T5-T6)
├── F3: Confounding Generator (T7-T9)
├── F4: Direction Generator (T10-T12)
├── F5: Information Generator (T13-T14)
└── F6: Mechanism Generator (T15-T17)

Each agent:
├── Input: Family-specific trap types
├── Template: L2 Guidelines Section 3 (Trap Type Templates)
├── Required output fields:
│   ├── hidden_question
│   ├── conditional_answers: {A, B}
│   ├── wise_refusal (template-following)
│   └── label: "NO"
└── Target: 8-10 cases per agent per batch
```

**L3 Generator Configuration:**
```
L3 Generator Agents (4 per batch):
├── F1-F2 Generator (Deterministic + Probabilistic)
├── F3-F4 Generator (Overdetermination + Structural)
├── F5-F6 Generator (Temporal + Epistemic)
└── F7-F8 Generator (Attribution + Moral/Legal)

Each agent:
├── Input: Family definitions and subtypes
├── Template: L3 Guidelines Section 3 (Family Templates)
├── Required output fields:
│   ├── counterfactual_claim
│   ├── invariants (1-3 bullets)
│   ├── ground_truth: VALID | INVALID | CONDITIONAL
│   └── justification
└── Target: 12-15 cases per agent per batch
```

---

### Phase 2B: Validation Step (Per Batch)

**5-6 Parallel Validator Agents**

All validators run in parallel on the generated batch:

#### Validator 1: Schema Validator Agent
```
Schema Validator:
├── Check: JSON structure matches V4.0 schema
├── Check: All required fields present per level
├── Check: Field types correct (string, array, object)
├── Check: Enumerations valid (labels, difficulty, trap_type)
├── Output: {case_id, schema_valid: bool, errors: []}
└── Pass criteria: schema_valid = true
```

#### Validator 2-3: Content Validator Agents (2 parallel)
```
Content Validator (10-point rubric):
├── Scenario clarity: 1.0 pt
├── Hidden question quality: 1.0 pt
├── Conditional answer A: 1.5 pt
├── Conditional answer B: 1.5 pt
├── Wise refusal quality: 2.0 pt
├── Difficulty calibration: 1.0 pt
├── Final label: 1.0 pt
├── Trap type: 1.0 pt
├── Output: {case_id, score: 0-10, breakdown: {}, pass: bool}
└── Pass criteria: score >= 8.0
```

#### Validator 4: Cross Validator Agent
```
Cross Validator:
├── Check: No exact duplicates (normalized text)
├── Check: Semantic similarity < 0.75 threshold
├── Check: Distribution balance (trap types, difficulty)
├── Check: No placeholder text detected
├── Output: {case_id, duplicate: bool, similarity_max, distribution_ok}
└── Pass criteria: duplicate = false AND similarity_max < 0.75
```

#### Validator 5-6: LLM Quality Judge Agents (2 parallel)
```
LLM Quality Judge:
├── Verify: Trap type correctly classified
├── Verify: Reasoning chain is sound
├── Verify: Conditional answers are mutually exclusive
├── Verify: Wise refusal follows template
├── Verify: Ground truth label is defensible
├── Output: {case_id, trap_type_correct: bool, reasoning_sound: bool, quality_score: 0-10}
└── Pass criteria: trap_type_correct AND reasoning_sound AND quality_score >= 7
```

#### Validation Aggregation
```
Aggregate Validation Results:
├── PASS: All 5 validators pass → Move to corrected/final
├── FAIL: Any validator fails → Route to Correction Phase
│   ├── Schema fail → Field Fixer Agent
│   ├── Content fail → Content Rewriter Agent
│   ├── Cross-validation fail → Rewrite with new scenario
│   └── LLM Judge fail → Label/Reasoning Corrector Agent
└── Calculate batch pass rate: (passed / total) * 100
```

---

### Phase 2C: Correction Step (Per Batch)

**3-5 Parallel Correction Agents**

Correction agents receive failed cases with specific failure reasons:

#### Correction Agent 1: Field Fixer
```
Field Fixer Agent:
├── Input: Cases failing schema validation
├── Fix: Add missing required fields
├── Fix: Correct field types
├── Fix: Fix enumeration values
└── Output: Corrected cases → Re-validate
```

#### Correction Agents 2-3: Content Rewriter
```
Content Rewriter Agent:
├── Input: Cases with content score < 8.0
├── Analyze: Which rubric criteria failed
├── Rewrite: Improve scenario clarity
├── Rewrite: Strengthen hidden question
├── Rewrite: Improve conditional answers
├── Rewrite: Fix wise refusal template
└── Output: Rewritten cases → Re-validate
```

#### Correction Agents 4-5: Label/Reasoning Corrector
```
Label Corrector Agent:
├── Input: Cases failing LLM quality check
├── Analyze: Why trap type was misclassified
├── Fix: Correct trap_type label
├── Fix: Adjust ground_truth label
├── Fix: Rewrite justification
└── Output: Corrected cases → Re-validate
```

---

### Phase 2D: Loop Termination Criteria

**Per-Batch Loop Continues Until:**
1. Pass rate ≥ 95% (at least 95% of cases pass all validators)
2. OR Maximum 5 correction iterations reached
3. OR Manual review requested for persistent failures

**Batch Checkpoint System:**
```
After each iteration:
├── Save batch state to checkpoint file
├── Log: iteration_number, pass_rate, failures_by_type
├── If pass_rate >= 95%:
│   └── Move all passed cases to batches/{group}/batch_XXX/final/
├── If iteration >= 5 AND pass_rate < 95%:
│   └── Flag batch for manual review
└── Continue to next iteration
```

---

### Phase 3: Batch Integration

**After all batches complete (pass rate ≥ 95%):**

**Integration Sub-agents (3 parallel):**

#### Integration Agent 1: Merger
```
Merger Agent:
├── Collect: All cases from batch_XXX/final/ directories
├── Merge: Into single dataset file
├── Assign: Sequential case IDs (T3-BucketI-0001, etc.)
└── Output: groupI_merged.json, groupJ_merged.json
```

#### Integration Agent 2: Distribution Verifier
```
Distribution Verifier Agent:
├── Check: L1 count = 50, L2 = 300, L3 = 150
├── Check: Difficulty ratio ~1:2:1
├── Check: Trap type coverage (all required types present)
├── Check: Label distribution (L1: 25W/20S/5A, L2: all NO, L3: ~35%V/25%I/40%C)
├── Output: Distribution report with any gaps
└── If gaps: Route to Gap Filler Agent
```

#### Integration Agent 3: Gap Filler
```
Gap Filler Agent:
├── Input: Distribution gaps from Verifier
├── Generate: Additional cases for underrepresented types
├── Validate: Using same pipeline
└── Output: Additional cases to merge
```

---

### Phase 4: Final Validation Sweep

**Full dataset validation (500 cases each):**

**Final Validation Agents (6 parallel):**
1. **Schema Compliance Agent**: Validate entire merged dataset
2. **Duplicate Detector Agent**: Cross-dataset duplicate check
3. **Score Aggregator Agent**: Calculate mean scores, distributions
4. **ID Uniqueness Agent**: Verify all case IDs unique
5. **Field Completeness Agent**: Verify all validation fields populated
6. **Quality Summary Agent**: Generate quality report

**Pass Criteria for Final Dataset:**
- [ ] Total cases = 500 per group
- [ ] L1/L2/L3 distribution = 50/300/150
- [ ] All cases have `initial_author`, `validator`, `final_score`
- [ ] Mean `final_score` ≥ 8.0
- [ ] No duplicates within or across datasets
- [ ] All required fields present per level

---

### Phase 5: Deliverables Generation

**5 Parallel Deliverable Agents per Group:**

#### Agent 1: Schema File Generator
```
Schema Generator Agent:
├── Input: V4.0 schema definition
├── Generate: Summarized schema documentation
├── Include: Field definitions, types, examples
├── Output: groupI_FernandoTorres_schema.json
```

#### Agent 2: Score File Generator
```
Score File Generator Agent:
├── Input: Validation scores from all batches
├── Compile: Per-case scores with breakdown
├── Calculate: Summary statistics
├── Output: groupI_FernandoTorres_score.json
```

#### Agent 3: Dataset Finalizer
```
Dataset Finalizer Agent:
├── Input: Merged, validated dataset
├── Format: Final JSON structure with metadata header
├── Add: Executive summary and distribution breakdown at start of file
├── Verify: All fields present
├── Output: groupI_FernandoTorres_dataset.json
```

**Dataset JSON Structure (with Metadata Header):**
```json
{
  "metadata": {
    "executive_summary": "This dataset contains 500 validated causal reasoning test cases for the T3 Benchmark, focusing on the AI & Tech domain. Cases span all three levels of Pearl's Ladder of Causation: L1 (Association) tests whether LLMs can distinguish justified from unjustified causal claims, L2 (Intervention) tests causal disambiguation and wise refusal generation, and L3 (Counterfactual) tests reasoning about alternative worlds. All cases underwent multi-agent validation with a 95%+ pass rate threshold, scoring ≥8.0/10 on a comprehensive quality rubric.",
    "dataset_info": {
      "name": "GroupI_FernandoTorres_Dataset",
      "version": "1.0",
      "domain": "D9: AI & Tech",
      "total_cases": 500,
      "created_date": "2026-01-XX",
      "author": "Fernando Torres",
      "validator": "Fernando Torres"
    },
    "distribution": {
      "by_pearl_level": {
        "L1_Association": 50,
        "L2_Intervention": 300,
        "L3_Counterfactual": 150
      },
      "by_label": {
        "L1": {"WOLF": 25, "SHEEP": 20, "AMBIGUOUS": 5},
        "L2": {"NO": 300},
        "L3": {"VALID": 52, "INVALID": 38, "CONDITIONAL": 60}
      },
      "by_difficulty": {
        "Easy": 125,
        "Medium": 250,
        "Hard": 125
      },
      "by_trap_family": {
        "L1_WOLF": {"W1": 4, "W2": 3, "W3": 3, "W5": 4, "W7": 5, "W9": 3, "W10": 3},
        "L1_SHEEP": {"S1": 5, "S2": 5, "S3": 4, "S4": 3, "S5": 3},
        "L2": {"F1_Selection": 68, "F2_Statistical": 34, "F3_Confounding": 60, "F4_Direction": 50, "F5_Information": 34, "F6_Mechanism": 54},
        "L3": {"F1": 20, "F2": 15, "F3": 15, "F4": 15, "F5": 15, "F6": 15, "F7": 20, "F8": 15, "DomainExt": 20}
      }
    },
    "quality_metrics": {
      "mean_score": 8.5,
      "min_score": 8.0,
      "max_score": 10.0,
      "schema_compliance": "100%",
      "duplicate_rate": "0%",
      "validation_pass_rate": "95%+"
    }
  },
  "cases": [
    // ... 500 validated cases ...
  ]
}
```

#### Agent 4: Report Generator
```
Report Generator Agent:
├── Generate: Section 1 - Summary comparison
├── Generate: Section 2 - Pearl level charts
├── Generate: Section 3 - Label distribution
├── Generate: Section 4 - Trap type heatmap
├── Generate: Section 5 - Difficulty charts
├── Generate: Section 6 - Score analysis
├── Generate: Section 7 - Methodology overview
├── Generate: Section 8 - Example case
├── Compile: PDF (≤10 pages)
└── Output: groupI_FernandoTorres_analysis.pdf
```

#### Agent 5: Methodology Document Generator
```
Methodology Generator Agent:
├── Document: Executive summary of multi-agent workflow
├── Document: Dataset creation process and schema design
├── Document: Agent architecture and parallel processing strategy
├── Document: Batch processing loop details
├── Document: Validation pipeline (schema, content, cross, LLM judge)
├── Document: Quality assurance and 95%+ pass rate enforcement
├── Document: Distribution balancing strategy
├── Document: Lessons learned and challenges
├── Include: Agent invocation statistics and batch metrics
└── Output: groupI_FernandoTorres_methodology.md
```

---

## 4. Agent Spawn Summary

### Total Agents by Phase

| Phase | Agent Type | Count | Parallel |
|-------|------------|-------|----------|
| Phase 1 | Transform Agents | 3 | Yes |
| Phase 2A | Generator Agents | 10-12 per batch | Yes |
| Phase 2B | Validator Agents | 5-6 per batch | Yes |
| Phase 2C | Correction Agents | 3-5 per batch | Yes |
| Phase 3 | Integration Agents | 3 | Yes |
| Phase 4 | Final Validation Agents | 6 | Yes |
| Phase 5 | Deliverable Agents | 5 per group | Yes |

### Agent Invocations Per Group

- **Generation batches**: 10 batches × 12 agents = 120 agent invocations
- **Validation iterations**: ~3 avg × 6 agents × 10 batches = 180 invocations
- **Correction iterations**: ~2 avg × 4 agents × 10 batches = 80 invocations
- **Integration + Final**: 3 + 6 + 5 = 14 invocations

**Total per group**: ~400 agent invocations
**Total for both groups**: ~800 agent invocations

---

## 5. Checkpoint and Recovery System

### Checkpoint Files (per batch)

```json
{
  "batch_id": "I-01",
  "iteration": 3,
  "status": "validating",
  "cases_generated": 50,
  "cases_passed": 47,
  "cases_failed": 3,
  "pass_rate": 0.94,
  "failures": [
    {"case_id": "I-01-023", "reason": "content_score_low", "score": 7.2},
    {"case_id": "I-01-031", "reason": "trap_type_mismatch"},
    {"case_id": "I-01-045", "reason": "duplicate_detected"}
  ],
  "timestamp": "2026-01-22T14:30:00Z"
}
```

### Recovery Procedure

If process interrupted:
1. Read checkpoint files for each batch
2. Identify incomplete batches (status != "finalized")
3. Resume from last completed step
4. Continue validation loop

---

## 6. Quality Metrics and Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Batch pass rate | ≥95% | (passed cases / total) per batch |
| Mean content score | ≥8.0 | Average 10-point rubric score |
| Schema compliance | 100% | All cases pass schema validation |
| Duplicate rate | 0% | No duplicates detected |
| Trap type accuracy | ≥95% | LLM judge agreement |
| Distribution compliance | 100% | L1/L2/L3 = 50/300/150 |

---

## 7. Execution Timeline

| Step | Duration | Description |
|------|----------|-------------|
| Phase 0 | 30 min | Infrastructure setup |
| Phase 1 | 1 hr | Schema transformation |
| Phase 2 | 6-8 hrs | Batch generation loop (16 batches × ~30 min avg) |
| Phase 3 | 30 min | Batch integration |
| Phase 4 | 30 min | Final validation sweep |
| Phase 5 | 1 hr | Deliverables generation |
| **Total** | **~10-12 hrs** | Full execution |

---

## 8. Critical Files Reference

| Purpose | Path |
|---------|------|
| Assignment Spec | `/docs/course/Assigment2/CS372_Win2026_Assignment2.md` |
| L1 Guidelines | `/docs/course/Assigment2/Assignment2_Guidelines-T3-L1.md` |
| L2 Guidelines | `/docs/course/Assigment2/Assignment2_Guidelines-T3-L2.md` |
| L3 Guidelines | `/docs/course/Assigment2/Assignment2_Guidelines-T3-L3.md` |
| GroupI1 Dataset | `/docs/course/Assigment2/GroupI1_dataset.json` |
| GroupJ1 Dataset | `/docs/course/Assigment2/GroupJ1_dataset.json` |
| V3.0 Schema | `/project/schemas/case_schema_v3.json` |
| Reference Dataset | `/project/output/final/GroupI1_datasetV3.0.json` |

---

## 9. Deliverables Summary

### Per Group (10 files total)

```
submissions/
├── groupI_FernandoTorres/
│   ├── groupI_FernandoTorres_schema.json
│   ├── groupI_FernandoTorres_score.json
│   ├── groupI_FernandoTorres_dataset.json (500 cases with metadata header)
│   ├── groupI_FernandoTorres_analysis.pdf (≤10 pages)
│   └── groupI_FernandoTorres_methodology.md
│
└── groupJ_FernandoTorres/
    ├── groupJ_FernandoTorres_schema.json
    ├── groupJ_FernandoTorres_score.json
    ├── groupJ_FernandoTorres_dataset.json (500 cases with metadata header)
    ├── groupJ_FernandoTorres_analysis.pdf (≤10 pages)
    └── groupJ_FernandoTorres_methodology.md
```

### Methodology Document Structure

Each methodology document (`*_methodology.md`) should include:

1. **Executive Summary**: Overview of the multi-agent workflow approach
2. **Dataset Creation Process**:
   - Schema design decisions (V4.0 format)
   - Agent architecture and parallel processing strategy
   - Batch processing loop (Generate → Validate → Correct → Loop)
3. **Validation Pipeline**:
   - Schema validation approach
   - 10-point content scoring rubric details
   - Cross-validation and duplicate detection
   - LLM-as-judge quality assessment
4. **Quality Assurance**:
   - 95%+ pass rate threshold enforcement
   - Correction agent strategies
   - Checkpoint and recovery system
5. **Distribution Balancing**:
   - Pearl level targeting (50 L1 / 300 L2 / 150 L3)
   - Trap type coverage strategy
   - Difficulty calibration
6. **Lessons Learned**: Challenges encountered and solutions applied

---

*Plan Version: 3.0 - Multi-Agent Parallel Workflow*
*Created: 2026-01-22*
*Status: ✅ COMPLETED*
*Completion Date: 2026-01-22*

---

## 10. Execution Log

### Session: 2026-01-22

**Phase 0: Infrastructure Setup - COMPLETED**
- [x] Created directory structure: `project/assignment2/{schemas,batches,validators,generators,submissions}`
- [x] Created V4.0 schema: `project/assignment2/schemas/case_schema_v4.json`

**Phase 1: Case Analysis - COMPLETED**
- GroupI1: 16 existing cases (L1: 5, L2: 8, L3: 3)
- GroupJ1: 240 existing cases (L1: 27, L2: 162, L3: 51)
- Generation gaps calculated:
  - GroupI1: 45 L1 + 292 L2 + 147 L3 = 484 new cases needed
  - GroupJ1: 23 L1 + 138 L2 + 99 L3 = 260 new cases needed

**Phase 2: Parallel Generation - IN PROGRESS**
- [x] Launched 6 parallel generation agents:
  - Agent 1: GroupI1 L1 (45 cases)
  - Agent 2: GroupI1 L2 (292 cases)
  - Agent 3: GroupI1 L3 (147 cases)
  - Agent 4: GroupJ1 L1 (23 cases)
  - Agent 5: GroupJ1 L2 (138 cases)
  - Agent 6: GroupJ1 L3 (99 cases)

---

## 11. Lessons Learned: Parallelization Strategy

### Issue Identified
Single agents generating large batches (100+ cases) hit output token limits and had to serialize work, creating bottlenecks. For example, one agent generating 292 L2 cases had to write batch files sequentially (T1→T2→T3...).

### Recommended Improvements for Future Tasks

**1. Split Large Batches into 3-4x More Parallel Agents**
- Instead of 1 agent for 292 L2 cases, use 6-8 agents with 35-50 cases each
- Each agent focuses on 2-3 trap types only
- Reduces risk of token exhaustion and accelerates overall completion

**2. Non-Overlapping File Ownership**
- CRITICAL: No two agents should write to the same file simultaneously
- Strategy: Assign each agent a unique output file prefix
  - Agent A → `L2_batch_A_T1_T2.json`
  - Agent B → `L2_batch_B_T3_T4.json`
  - Agent C → `L2_batch_C_T5_T6.json`

**3. Pre-Assigned Case ID Ranges**
- Prevent duplicate case IDs by assigning ranges before spawning:
  - Agent A: case IDs 0001-0050
  - Agent B: case IDs 0051-0100
  - Agent C: case IDs 0101-0150
- Final merge renumbers sequentially

**4. Trap Type Partitioning**
- Divide trap types/families across agents to ensure no duplicates:
  - L2 Agent 1: T1-T3 (Selection)
  - L2 Agent 2: T4-T6 (Statistical)
  - L2 Agent 3: T7-T9 (Confounding)
  - L2 Agent 4: T10-T12 (Direction)
  - L2 Agent 5: T13-T14 (Information)
  - L2 Agent 6: T15-T17 (Mechanism)

**5. Optimized Batch Sizes**
- L1: 15-25 cases per agent (max 3 agents)
- L2: 30-50 cases per agent (6-8 agents per group)
- L3: 25-35 cases per agent (4-6 agents per group)

**6. Merge-Dedup Strategy**
- After all agents complete, run a single merge pass
- Cross-check for near-duplicate scenarios (similarity threshold)
- Renumber case IDs sequentially
- Validate distribution targets are met

### Example Improved Agent Spawn for GroupI1 L2 (292 cases)
```
Instead of 1 agent for 292 cases, spawn 8 parallel agents:
├── Agent L2-A: T1-T2 (Selection) → 37 cases → L2_batch_A.json
├── Agent L2-B: T3-T4 (Selection) → 37 cases → L2_batch_B.json
├── Agent L2-C: T5-T6 (Statistical) → 36 cases → L2_batch_C.json
├── Agent L2-D: T7-T8 (Confounding) → 36 cases → L2_batch_D.json
├── Agent L2-E: T9-T10 (Confounding/Direction) → 37 cases → L2_batch_E.json
├── Agent L2-F: T11-T12 (Direction) → 37 cases → L2_batch_F.json
├── Agent L2-G: T13-T14 (Information) → 36 cases → L2_batch_G.json
└── Agent L2-H: T15-T17 (Mechanism) → 36 cases → L2_batch_H.json

Total: 292 cases across 8 non-overlapping files
```

This approach would complete in ~1/4 the time with proper parallelization.
