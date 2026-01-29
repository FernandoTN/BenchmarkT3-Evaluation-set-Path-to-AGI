# GroupI Migration Report

**Author:** Fernando Torres
**Date:** 2026-01-28
**Dataset:** groupI_FernandoTorres_dataset.json

---

## Summary

| Metric | Before Migration | After Migration |
|--------|------------------|-----------------|
| Total Cases | 500 | 500 |
| Schema Version | Pre-remediation | T3 Benchmark V3.0 |
| Pearl Levels | L1, L2, L3 | L1, L2, L3 |
| Required Fields | Partial | Complete |

---

## Pearl Level Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| L1 | 50 | 10.0% |
| L2 | 300 | 60.0% |
| L3 | 150 | 30.0% |
| **Total** | **500** | **100%** |

---

## Label Distribution

### Level 1 (Association)
| Label | Count |
|-------|-------|
| YES | 15 |
| NO | 30 |
| AMBIGUOUS | 5 |
| **Subtotal** | **50** |

### Level 2 (Intervention)
| Label | Count |
|-------|-------|
| NO | 300 |
| **Subtotal** | **300** |

### Level 3 (Counterfactual)
| Label | Count |
|-------|-------|
| VALID | 54 |
| INVALID | 33 |
| CONDITIONAL | 63 |
| **Subtotal** | **150** |

---

## Trap Type Distribution

| Trap Type | Count | Description |
|-----------|-------|-------------|
| T12 | 30 | Causal Trap Type 12 |
| T13 | 26 | Causal Trap Type 13 |
| T15 | 26 | Causal Trap Type 15 |
| T11 | 24 | Causal Trap Type 11 |
| T14 | 24 | Causal Trap Type 14 |
| T1 | 24 | Causal Trap Type 1 |
| F1 | 21 | Formal Logic Trap 1 |
| T10 | 20 | Causal Trap Type 10 |
| F7 | 20 | Formal Logic Trap 7 |
| T2 | 19 | Causal Trap Type 2 |
| T5 | 19 | Causal Trap Type 5 |
| T3 | 17 | Causal Trap Type 3 |
| DomainExt | 17 | Domain Extension Trap |
| T6 | 16 | Causal Trap Type 6 |
| F2 | 16 | Formal Logic Trap 2 |
| F4 | 16 | Formal Logic Trap 4 |
| T4 | 15 | Causal Trap Type 4 |
| F3 | 15 | Formal Logic Trap 3 |
| F5 | 15 | Formal Logic Trap 5 |
| F6 | 15 | Formal Logic Trap 6 |
| F8 | 15 | Formal Logic Trap 8 |
| T7 | 8 | Causal Trap Type 7 |
| T16 | 8 | Causal Trap Type 16 |
| T17 | 8 | Causal Trap Type 17 |
| T8 | 8 | Causal Trap Type 8 |
| T9 | 8 | Causal Trap Type 9 |
| W7 | 6 | World Knowledge Trap 7 |
| W5 | 5 | World Knowledge Trap 5 |
| A | 5 | Ambiguity Trap |
| W3 | 4 | World Knowledge Trap 3 |
| S1 | 4 | Statistical Trap 1 |
| W1 | 4 | World Knowledge Trap 1 |
| W2 | 3 | World Knowledge Trap 2 |
| W9 | 3 | World Knowledge Trap 9 |
| W10 | 3 | World Knowledge Trap 10 |
| S2 | 3 | Statistical Trap 2 |
| S3 | 3 | Statistical Trap 3 |
| S4 | 3 | Statistical Trap 4 |
| S5 | 2 | Statistical Trap 5 |
| W4 | 1 | World Knowledge Trap 4 |
| W6 | 1 | World Knowledge Trap 6 |

---

## Difficulty Distribution

| Difficulty | Count | Percentage |
|------------|-------|------------|
| Easy | 129 | 25.8% |
| Medium | 206 | 41.2% |
| Hard | 165 | 33.0% |
| **Total** | **500** | **100%** |

---

## Domain Distribution

| Domain | Count | Percentage |
|--------|-------|------------|
| D9 (AI/ML) | 500 | 100% |

---

## Score Summary

| Metric | Value |
|--------|-------|
| Mean Score | 8.52 |
| Min Score | 8.0 |
| Max Score | 9.5 |

---

## Prompt Setup

This section documents the prompt engineering approach, LLM configuration, and generation methodology used for the GroupI (AI & Tech) dataset.

### LLM Configuration

| Parameter | Value |
|-----------|-------|
| Model | Claude (Anthropic) |
| Temperature | 0.7 (generation), 0.0 (validation) |
| Max Tokens | 4096 per case |
| Context Window | Full conversation context |

### Generation Methodology

The dataset was created using a **multi-agent parallel workflow** designed to maximize throughput while maintaining rigorous quality standards:

1. **Generator Agents (10-12 parallel)**: Specialized by trap type family
   - L1 Generators: WOLF (W1-W10) and SHEEP (S1-S8) specialists
   - L2 Generators: One per family (F1-F6, covering T1-T17)
   - L3 Generators: Covering F1-F8 counterfactual families

2. **Validation Agents (5-6 parallel)**:
   - Schema Validator: JSON structure compliance
   - Content Validators: 10-point rubric scoring
   - Cross Validator: Duplicate detection and distribution balance
   - LLM Quality Judges: Trap type verification and reasoning soundness

3. **Correction Agents (3-5 parallel)**:
   - Field Fixer: Schema compliance fixes
   - Content Rewriter: Improve scenario/refusal quality
   - Label Corrector: Fix trap type and label misclassifications

### Quality Control Measures

- **95%+ Pass Rate Threshold**: Each batch required minimum 95% validation pass rate
- **10-Point Rubric Scoring**: Cases scored on scenario clarity, hidden question quality, conditional answers, wise refusal quality, difficulty calibration, final label, and trap type
- **Acceptance Threshold**: Score ≥ 8.0 required for acceptance
- **Duplicate Detection**: Semantic similarity threshold < 0.75
- **Iterative Correction Loop**: Failed cases routed to correction agents until threshold met

### Prompt Templates

**L1 Generator Prompt Structure:**
- Domain context (AI & Technology)
- Trap type definition and examples
- Variable structure requirements (X, Y, Z)
- Label guidelines (YES/NO/AMBIGUOUS mapping)

**L2 Generator Prompt Structure:**
- Intervention scenario requirements
- Hidden question formulation guidelines
- Conditional answer mutual exclusivity requirements
- Wise refusal template structure

**L3 Generator Prompt Structure:**
- Counterfactual claim formulation
- Invariant specification guidelines
- Ground truth evaluation criteria (VALID/INVALID/CONDITIONAL)

---

## Schema Changes Applied

The following schema changes were applied during migration:

1. **Standardized ID Format**: All case IDs follow pattern `T3-BucketLarge-I-{level}.{case_id}`
2. **Pearl Level Prefix**: Changed from numeric (1, 2, 3) to prefixed format (L1, L2, L3)
3. **Required Fields Validated**: All 16 required fields present in every case
4. **Trap Object Structure**: Standardized trap field as object with `type` and `description`
5. **Variables Object**: Ensured consistent structure with X, Y, and optional Z variables
6. **Label Standardization**: L1 uses YES/NO/AMBIGUOUS, L2 uses NO, L3 uses VALID/INVALID/CONDITIONAL

---

## Example Cases

### Level 1 Example (Association)

```json
{
  "id": "T3-BucketLarge-I-1.1",
  "case_id": "0001",
  "pearl_level": "L1",
  "domain": "D9",
  "subdomain": "AI Scaling",
  "difficulty": "Easy",
  "label": "NO",
  "trap": {
    "type": "W3",
    "description": "World knowledge trap - overgeneralization"
  },
  "scenario": "Larger models (X) correlate with higher truthfulness scores (Y) on benchmarks. A user assumes a 100B model never lies...",
  "claim": "A 100 billion parameter model never produces false statements because larger models correlate with higher truthfulness scores."
}
```

### Level 2 Example (Intervention)

```json
{
  "id": "T3-BucketLarge-I-2.100",
  "case_id": "0100",
  "pearl_level": "L2",
  "domain": "D9",
  "subdomain": "Dynamic Pricing",
  "difficulty": "Medium",
  "label": "NO",
  "trap": {
    "type": "T11",
    "description": "Causal trap - feedback loop confusion"
  },
  "scenario": "A dynamic pricing algorithm shows that high prices are charged when demand is high, concluding it optimally captures value. However, high prices may suppress demand...",
  "claim": "The dynamic pricing algorithm optimally matches prices to market demand."
}
```

### Level 3 Example (Counterfactual)

```json
{
  "id": "T3-BucketLarge-I-3.351",
  "case_id": "0351",
  "pearl_level": "L3",
  "domain": "D9",
  "subdomain": "Deep Learning Dynamics",
  "difficulty": "Easy",
  "label": "INVALID",
  "trap": {
    "type": "F1",
    "description": "Formal logic trap - unfalsifiable counterfactual"
  },
  "scenario": "Training loss spiked to NaN (X) and the run was stopped (Y). Claim: if we let it run one more epoch, it would have converged...",
  "claim": "If we let the training run one more epoch after the NaN loss spike, it would have converged."
}
```

---

## Migration Status

- [x] Dataset migrated to V3.0 schema
- [x] All 500 cases validated
- [x] Pearl level distribution verified (L1:50, L2:300, L3:150)
- [x] All required fields present
- [x] Schema file generated
- [x] Score file preserved

**Migration Complete**
